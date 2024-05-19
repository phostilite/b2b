from django import forms
from django.contrib.auth.models import User

from .models import Cart, CartItem
from stock.models import Product, SizeGroup
        
class CartItemForm(forms.Form):
    product_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1)
    size_groups = forms.ModelMultipleChoiceField(queryset=SizeGroup.objects.all())  