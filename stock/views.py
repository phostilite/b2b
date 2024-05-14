from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.forms import modelformset_factory
from django.contrib import messages
from django.shortcuts import get_object_or_404

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
    
    colors = [color.name for color in product.colors.all()]
    size_groups = [{'name': size_group.name, 'sizes': [size.name for size in size_group.sizes.all()]} for size_group in product.available_size_groups.all()]
    images = [request.build_absolute_uri(image.image.url) for image in product.images.all()]

    data = {
        'id': product.id,
        'title': product.title,
        'description': product.description,
        'design_number': product.design_number,
        'type': product.type,
        'colors': colors,
        'size_groups': size_groups,
        'images': images,
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


@login_required
def update_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    ImageFormSet = modelformset_factory(ProductImage, form=ProductImageForm, extra=1)

    if request.method == "POST":
        form = ProductUpdateForm(request.POST, instance=product)
        formset = ImageFormSet(request.POST, request.FILES, queryset=ProductImage.objects.filter(product=product))
        if (
            "HTTP_X_REQUESTED_WITH" in request.META
            and request.META["HTTP_X_REQUESTED_WITH"] == "XMLHttpRequest"
        ):  # Handle AJAX form submission
            if form.is_valid() and formset.is_valid():
                form.save()
                images = formset.save(commit=False)
                for image in images:
                    image.product = product
                    image.save()
                return JsonResponse({"success": True})
            else:
                errors = form.errors
                for form_errors in formset.errors:
                    errors.update(form_errors)
                return JsonResponse({"success": False, "errors": errors})
        else:
            if form.is_valid() and formset.is_valid():
                form.save()
                images = formset.save(commit=False)
                for image in images:
                    image.product = product
                    image.save()
                messages.success(request, "Product updated successfully")
                return redirect("product-list")
    else:
        form = ProductUpdateForm(instance=product)
        formset = ImageFormSet(queryset=ProductImage.objects.filter(product=product))

    return render(request, "admin/product_list.html", {"form": form, "formset": formset})