from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.forms import modelformset_factory
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Product, ProductImage, Size, SizeGroup, Color
from .forms import ProductForm, ProductImageForm, ProductUpdateForm

import logging

logger = logging.getLogger(__name__)

@login_required
def product_list_view(request):
    if request.user.groups.filter(name='Admin').exists():
        products = Product.objects.all()
        return render(request, 'admin/product_list.html', {'products': products}) 
    elif request.user.groups.filter(name='Dealer').exists():
        products = Product.objects.all()
        return render(request, 'dealer/product_list.html', {'products': products})
    
@login_required    
def product_detail_view(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    all_colors = product.colors.all()
    selected_colors = [color.name for color in product.colors.all()]

    all_size_groups = product.available_size_groups.all()
    selected_size_groups = [size_group.name for size_group in product.available_size_groups.all()]
        
    all_colors = [
        {
            'name': color.name,
            'hex_code': color.hex_code,
            'selected': color.name in selected_colors
        }
        for color in Color.objects.all()
    ]
    
    all_size_groups = [
        {
            'name': size_group.name, 
            'sizes': [size.name for size in size_group.sizes.all()],
            'selected': size_group.name in selected_size_groups
        } 
        for size_group in SizeGroup.objects.all()
    ]

    data = {
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'design_number': product.design_number,
        'type': product.type,
        'all_colors': all_colors,
        'all_size_groups': all_size_groups,
        'current_stock': product.current_stock,
        'mrp': product.mrp,
        'dealer_price': product.dealer_price,
    }
    return JsonResponse(data)

@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        image_form = ProductImageForm(request.POST, request.FILES)
        if form.is_valid() and image_form.is_valid():
            product = form.save()
            ProductImage.objects.create(product=product, **image_form.cleaned_data)
            return redirect('product_list')
        else:
            logger.error(f'ProductForm errors: {form.errors}')
            logger.error(f'ProductImageForm errors: {image_form.errors}')
    else:
        form = ProductForm()
        image_form = ProductImageForm()
    return render(request, 'admin/create_product.html', {'form': form, 'image_form': image_form})

@csrf_exempt
@login_required
@require_POST
def product_update_view(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)

    data = json.loads(request.body)

    product.title = data.get('title', product.title)
    product.description = data.get('description', product.description)
    product.design_number = data.get('design_number', product.design_number)
    product.type = data.get('type', product.type)
    product.current_stock = data.get('current_stock', product.current_stock)
    product.mrp = data.get('mrp', product.mrp)
    product.dealer_price = data.get('dealer_price', product.dealer_price)

    # Update colors
    selected_colors = data.get('all_colors', [])
    product.colors.clear()
    for color_name in selected_colors:
        color, created = Color.objects.get_or_create(name=color_name)
        product.colors.add(color)

    # Update size groups
    selected_size_groups = data.get('all_size_groups', [])
    product.available_size_groups.clear()
    for size_group_name in selected_size_groups:
        size_group, created = SizeGroup.objects.get_or_create(name=size_group_name)
        product.available_size_groups.add(size_group)

    product.save()

    return JsonResponse({'status': 'success', 'message': 'Product updated successfully'})