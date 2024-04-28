from django.shortcuts import render
from django.contrib.auth.decorators import login_required

import logging

logger = logging.getLogger(__name__)

from .models import Order, OrderItem, OrderHistory, BillingAddress, ShippingAddress
from dealers.models import Dealer
from sales.models import Employee
from retailers.models import Retailer
from cart.models import Cart, CartItem
from administration.models import AdminUser

from .forms import OrderForm, BillingAddressFormSet, ShippingAddressFormSet
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import allowed_users

from .utils import generate_order_number, generate_order_name, generate_order_description

@login_required
@allowed_users(allowed_roles=["Admin", "Sales", "Dealer"])
def order_list_view(request):
    try:
        if request.user.groups.filter(name='Admin').exists():
            orders = Order.objects.all()
            return render(request, 'admin/order_list.html', {'orders': orders})
        elif request.user.groups.filter(name='Sales').exists():
            try:
                employee = Employee.objects.get(user=request.user)
                orders = Order.objects.filter(sales=employee)
            except Employee.DoesNotExist:
                return render(request, 'error.html', {'message': 'Employee does not exist.'})
            return render(request, 'employee/order_list.html', {'orders': orders})
        elif request.user.groups.filter(name='Dealer').exists():
            try:
                dealer = Dealer.objects.get(user=request.user)
                orders = Order.objects.filter(dealer=dealer)
            except Dealer.DoesNotExist:
                return render(request, 'error.html', {'message': 'Dealer does not exist.'})
            return render(request, 'dealer/order_list.html', {'orders': orders})
        else:
            return render(request, 'error.html', {'message': 'You do not have permission to view this page.'})
    except Exception as e:
        logger.error(f'Error in order_list_view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})


import logging

logger = logging.getLogger(__name__)

@login_required
@allowed_users(allowed_roles=["Dealer"])
def create_order(request):
    try:
        if request.method == 'POST':
            form = OrderForm(request.user, request.POST)
            billing_formset = BillingAddressFormSet(request.POST, prefix='billing')
            shipping_formset = ShippingAddressFormSet(request.POST, prefix='shipping')
            if form.is_valid() and billing_formset.is_valid() and shipping_formset.is_valid():
                order = form.save(commit=False)
                order.dealer = request.user.dealer
                order.employee = None  
                order.admin = AdminUser.objects.first()  
                order.order_date = timezone.now()
                order.status = 'Pending'
                order.order_number = generate_order_number()  
                order.name = generate_order_name(order.order_number)  
                order.description = generate_order_description()  
                order.save()

                billing_formset.instance = order
                billing_formset.save()
                shipping_formset.instance = order
                shipping_formset.save()

                request.session['order_id'] = order.id

                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                grand_total = 0
                for item in cart_items:
                    order_item = OrderItem.objects.create(
                        order=order, 
                        product=item.product, 
                        quantity=item.quantity, 
                        net_amount=item.product_price_by_size_group
                    )
                    grand_total += order_item.net_amount

                order.grand_total_amount = grand_total
                order.save()
                
                cart_items.delete()  

                return redirect('dealer_order_list')  
            else:
                logger.debug("Form errors:")
                logger.debug(form.errors)
                logger.debug("Billing formset errors:")
                logger.debug(billing_formset.errors)
                logger.debug("Shipping formset errors:")
                logger.debug(shipping_formset.errors)

                logger.debug("POST data:")
                logger.debug(request.POST)
        else:
            form = OrderForm(request.user)
            billing_formset = BillingAddressFormSet(prefix='billing')
            shipping_formset = ShippingAddressFormSet(prefix='shipping')
        return render(request, 'dealer/create_order.html', {
            'form': form, 
            'billing_formset': billing_formset,
            'shipping_formset': shipping_formset,
        })
    except Exception as e:
        logger.error(f'Error in create_order: {e}')
        return render(request, 'error.html', {'message': 'An error occurred while creating the order.'})