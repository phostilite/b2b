from django.shortcuts import render, redirect

from .models import Product, ProductImage, Size, SizeGroup, Color
from .forms import ProductForm, ProductImageForm

import logging

logger = logging.getLogger(__name__)

def product_list_view(request):
    if request.user.groups.filter(name='Admin').exists():
        products = Product.objects.all()
        return render(request, 'admin/product_list.html', {'products': products}) 
    elif request.user.groups.filter(name='Dealer').exists():
        products = Product.objects.all()
        return render(request, 'dealer/product_list.html', {'products': products})

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