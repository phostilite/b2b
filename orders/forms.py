from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User

from .models import Order, Retailer, BillingAddress, ShippingAddress

BillingAddressFormSet = inlineformset_factory(Order, BillingAddress, 
    fields=('first_name', 'last_name', 'company', 'address_1', 'address_2', 'city', 'state', 'postcode', 'country', 'email', 'phone'), 
    extra=1, can_delete=False)

ShippingAddressFormSet = inlineformset_factory(Order, ShippingAddress, 
    fields=('first_name', 'last_name', 'company', 'address_1', 'address_2', 'city', 'state', 'postcode', 'country', 'email', 'phone'), 
    extra=1, can_delete=False)

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['retailer']

    def __init__(self, dealer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['retailer'].queryset = Retailer.objects.filter(created_by__dealer=dealer.dealer)