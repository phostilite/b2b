from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

import logging

logger = logging.getLogger(__name__)

from .models import Order, OrderItem, OrderHistory, BillingAddress, ShippingAddress
from dealers.models import Dealer
from sales.models import Employee
from retailers.models import Retailer
from cart.models import Cart, CartItem
from administration.models import AdminUser
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist

from .forms import DealerOrderForm, EmployeeOrderForm, BillingAddressFormSet, ShippingAddressFormSet
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
                orders = Order.objects.filter(created_by=employee.user)
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



@login_required
@allowed_users(allowed_roles=["Dealer", "Sales"])
def create_order(request):
    logger.info(f'Creating order for user {request.user.username}')
    try:
        if request.method == 'POST':
            logger.debug('Before form creation')
            if request.user.groups.filter(name="Dealer").exists():
                dealer = Dealer.objects.get(user=request.user)
                form = DealerOrderForm(dealer, request.POST)
            elif request.user.groups.filter(name="Sales").exists():
                employee = Employee.objects.get(user=request.user)
                form = EmployeeOrderForm(employee, request.POST)
            else:
                return HttpResponseForbidden("You do not have permission to create an order.")
            logger.debug('After form creation')
            billing_formset = BillingAddressFormSet(request.POST, prefix='billing')
            shipping_formset = ShippingAddressFormSet(request.POST, prefix='shipping')
            if form.is_valid() and billing_formset.is_valid() and shipping_formset.is_valid():
                order = form.save(commit=False)
                
                try:
                    if request.user.groups.filter(name="Dealer").exists():
                            dealer = Dealer.objects.get(user=request.user)
                            order.dealer = dealer
                except Dealer.DoesNotExist:
                    order.dealer = None

                try:
                    if request.user.groups.filter(name="Sales").exists():
                        employee = Employee.objects.get(user=request.user)
                        order.employee = employee
                    else:
                        order.employee = None
                except Employee.DoesNotExist:
                    order.employee = None
                    
                logger.info(f'Order created by user {request.user.username}')
                    
                order.admin = AdminUser.objects.first()  
                order.created_by = request.user
                order.order_date = timezone.now()
                order.status = 'Pending Approval'
                order.order_number = generate_order_number()  
                order.name = generate_order_name(order.order_number)  
                order.payment_status = 'Not Paid'
                order.save()

                billing_formset.instance = order
                billing_formset.save()
                shipping_formset.instance = order
                shipping_formset.save()

                request.session['order_id'] = order.id

                cart = Cart.objects.get(user=request.user)
                cart_items = CartItem.objects.filter(cart=cart)
                
                order.description = generate_order_description(cart_items)  
                
                grand_total = 0
                for item in cart_items:
                    order_item = OrderItem.objects.create(
                        order=order, 
                        product=item.product, 
                        quantity=item.quantity, 
                        item_size_group=item.size_groups.first(),
                        unit_price = item.product_price,
                        total_amount=item.product_price_by_size_group,
                        net_amount=item.product_price * item.quantity
                    )
                    grand_total += order_item.net_amount

                order.grand_total_amount = grand_total
                order.save()
                
                cart_items.delete()  

                if order.created_by.groups.filter(name="Dealer").exists():
                    return redirect('order_confitmation')  
                else:
                    return redirect('employee_order_confirmation')
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
            try:
                if request.user.groups.filter(name="Dealer").exists():
                    dealer = Dealer.objects.get(user=request.user)
                    form = DealerOrderForm(dealer)
                elif request.user.groups.filter(name="Sales").exists():
                    employee = Employee.objects.get(user=request.user)
                    form = EmployeeOrderForm(employee)
                else:
                    return HttpResponseForbidden("You do not have permission to create an order.")
            except ObjectDoesNotExist:
                return HttpResponseForbidden("You do not have an associated Dealer or Employee object.")
            billing_formset = BillingAddressFormSet(prefix='billing')
            shipping_formset = ShippingAddressFormSet(prefix='shipping')
        template_path = 'dealer/create_order.html' if request.user.groups.filter(name="Dealer").exists() else 'employee/create_order.html'
        return render(request, template_path, {
            'form': form,
            'billing_formset': billing_formset,
            'shipping_formset': shipping_formset,
        })
    except Exception as e:
        logger.error(f'Error in create_order: {e}')
        return render(request, 'error.html', {'message': 'An error occurred while creating the order.'})
    
    
@login_required
@allowed_users(allowed_roles=["Admin", "Sales", "Dealer"])
def order_details_view(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        billing_address = order.billing_addresses.first()  
        shipping_address = order.shipping_addresses.first()  
        order_items = order.orderitem_set.all()  

        context = {
            'order': order,
            'billing_address': billing_address,
            'shipping_address': shipping_address,
            'order_items': order_items,
        }

        return render(request, 'admin/order_details.html', context)

    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} does not exist.')
        return render(request, 'error.html', {'message': 'Order does not exist.'})

    except Exception as e:
        logger.error(f'Error in order_details_view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})
    
@require_POST
@login_required
@allowed_users(allowed_roles=["Admin"])
def approve_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.is_approved = True
        order.status = 'Approved'
        order.save()

        return redirect('order_details', order_id=order.id)

    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} does not exist.')
        return render(request, 'error.html', {'message': 'Order does not exist.'})

    except Exception as e:
        logger.error(f'Error in approve_order: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})
    
    
def order_confirmation_view(request):
    try:
        order_id = request.session.get('order_id')
        order = Order.objects.get(id=order_id)

        billing_address = order.billing_addresses.first()
        shipping_address = order.shipping_addresses.first()
        order_items = order.orderitem_set.all()

        is_dealer = request.user.groups.filter(name="Dealer").exists()
        is_employee = request.user.groups.filter(name="Sales").exists()

        context = {
            'order': order,
            'billing_address': billing_address,
            'shipping_address': shipping_address,
            'order_items': order_items,
            'is_dealer': is_dealer,
            'is_employee': is_employee,
        }

        if is_dealer:
            return render(request, 'dealer/order_confirmation.html', context)
        elif is_employee:
            return render(request, 'employee/order_confirmation.html', context)
        else:
            # Handle the case when the user is not a Dealer or Employee
            return render(request, 'error.html', {'message': 'Access denied.'})

    except Order.DoesNotExist:
        logger.error(f'Order with id {order_id} does not exist.')
        return render(request, 'error.html', {'message': 'Order does not exist.'})

    except Exception as e:
        logger.error(f'Error in order_confirmation_view: {e}')
        return render(request, 'error.html', {'message': 'An error occurred.'})