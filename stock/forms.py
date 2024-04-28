from django import forms
from .models import Product, ProductImage

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'type': forms.Select,
            'colors': forms.CheckboxSelectMultiple,
            'available_size_groups': forms.CheckboxSelectMultiple,
        }
        
class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']