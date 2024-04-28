import logging
from django.shortcuts import render, redirect
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from stock.models import Product, SizeGroup
from .models import Cart, CartItem
from .forms import CartItemForm
from accounts.decorators import allowed_users
from django.contrib.auth.decorators import login_required

# Create a logger
logger = logging.getLogger(__name__)

@login_required
@allowed_users(allowed_roles=["Dealer"])
def add_to_cart(request):
    if request.method == 'POST':
        form = CartItemForm(request.POST)
        if form.is_valid():
            product_id = form.cleaned_data.get('product_id')
            quantity = form.cleaned_data.get('quantity')
            size_groups = form.cleaned_data.get('size_groups') 
            logger.info(f'Product ID: {product_id}, Quantity: {quantity}, Size Groups: {size_groups}')
            
            cart, created = Cart.objects.get_or_create(user=request.user, defaults={'created_at': timezone.now()})
            if created:
                logger.info(f'New cart created for user: {request.user}')
            else:
                logger.info(f'Existing cart found for user: {request.user}')
            
            product = Product.objects.get(id=product_id)
            logger.info(f'Product retrieved: {product}')
            
            # Check if a cart item with the same product and size groups already exists
            cart_item = CartItem.objects.filter(cart=cart, product=product, size_groups__in=size_groups).first()
            if cart_item and len(cart_item.size_groups.all()) == len(size_groups):
                # If it exists and size groups are the same, increment the quantity
                cart_item.quantity += quantity
                logger.info(f'Existing item updated in cart: {product}, New Quantity: {cart_item.quantity}')
            else:
                # If it doesn't exist or size groups are different, create a new cart item
                cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
                cart_item.size_groups.set(size_groups)
                logger.info(f'New item added to cart: {product}, Quantity: {quantity}, Size Groups: {size_groups}')
            
            total_sizes = sum([len(size_group.sizes.all()) for size_group in cart_item.size_groups.all()])
            if product.dealer_price is not None:  
                cart_item.product_price = product.dealer_price
                cart_item.product_price_by_size_group = product.dealer_price * total_sizes  * cart_item.quantity
            else:
                logger.error(f'dealer_price is None for product: {product}')
                return render(request, 'dealer/product_list.html', {'form': form, 'error': 'Dealer price is not set for the product.'})
            
            cart_item.save()
            
            return redirect('dealer_product_list')  
        else:
            logger.error(f'Form validation errors: {form.errors}')
    return render(request, 'dealer/product_list.html')

@login_required
@allowed_users(allowed_roles=["Dealer"])
def view_cart(request):
    try:
        cart = Cart.objects.get(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)
        cart_items_list = [
            {
                'product': str(item.product), 
                'quantity': item.quantity, 
                'image': item.product.images.first().image.url if item.product.images.first() else None,
                'price': item.product.dealer_price,
                'price_by_size_group': item.product_price_by_size_group,
                'product_id': item.product.id,
                'size_groups': [
                    {
                        'id': size_group.id,
                        'name': size_group.name,
                        'sizes': [size.name for size in size_group.sizes.all()]
                    }
                    for size_group in item.size_groups.all()
                ],
            } 
            for item in cart_items
        ]
    except Cart.DoesNotExist:
        cart_items_list = []

    return JsonResponse({'cart_items': cart_items_list})

@require_http_methods(["DELETE"])
def delete_from_cart(request, product_id, size_group_id=None):
    try:
        logger.info(f'Received DELETE request for product ID: {product_id}')
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.get(user=request.user)
        if size_group_id is not None:
            size_group = SizeGroup.objects.get(id=size_group_id)
            cart_item = CartItem.objects.get(cart=cart, product=product, size_groups=size_group)
        else:
            cart_item = CartItem.objects.get(cart=cart, product=product)
        cart_item.delete()
        logger.info(f'Deleted product from cart: {product_id}')
        return JsonResponse({'status': 'success'}, status=200)
    except Product.DoesNotExist:
        logger.error(f'Product with ID {product_id} does not exist')
        return JsonResponse({'status': 'error', 'message': 'Product not found'}, status=404)
    except Cart.DoesNotExist:
        logger.error(f'Cart for user {request.user} does not exist')
        return JsonResponse({'status': 'error', 'message': 'Cart not found'}, status=404)
    except CartItem.DoesNotExist:
        logger.error(f'CartItem for product ID {product_id} and user {request.user} does not exist')
        return JsonResponse({'status': 'error', 'message': 'CartItem not found'}, status=404)
    except SizeGroup.DoesNotExist:
        logger.error(f'Size group with ID {size_group_id} does not exist')
        return JsonResponse({'status': 'error', 'message': 'Size group not found'}, status=404)
    
    
    
