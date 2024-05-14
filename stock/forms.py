from django import forms
from .models import Product, ProductImage, SizeGroup, Color

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
        
class ProductUpdateForm(forms.ModelForm):
    colors = forms.ModelMultipleChoiceField(queryset=Color.objects.all(), widget=forms.CheckboxSelectMultiple)
    available_size_groups = forms.ModelMultipleChoiceField(queryset=SizeGroup.objects.all(), widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = Product
        fields = ['title', 'description', 'design_number', 'type', 'colors', 'available_size_groups', 'current_stock', 'mrp', 'dealer_price']

    def __init__(self, *args, **kwargs):
        super(ProductUpdateForm, self).__init__(*args, **kwargs)
        if self.instance:
            self.fields['colors'].initial = self.instance.colors.all()
            self.fields['available_size_groups'].initial = self.instance.available_size_groups.all()