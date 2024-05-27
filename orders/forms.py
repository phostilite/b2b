from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.models import User

from .models import Order, BillingAddress, ShippingAddress
from retailers.models import Retailer
from dealers.models import Dealer

BillingAddressFormSet = inlineformset_factory(Order, BillingAddress, 
    fields=('full_name', 'address_1', 'address_2', 'city', 'state', 'postcode', 'country', 'email', 'phone'), 
    extra=1, can_delete=False)

ShippingAddressFormSet = inlineformset_factory(Order, ShippingAddress, 
    fields=('full_name', 'address_1', 'address_2', 'city', 'state', 'postcode', 'country', 'email', 'phone'), 
    extra=1, can_delete=False)

class DealerOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['retailer']

    def __init__(self, dealer, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['retailer'].queryset = Retailer.objects.filter(created_by__dealer=dealer)
        
class EmployeeOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['retailer', 'dealer']

    def __init__(self, employee, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['retailer'].queryset = Retailer.objects.all()
        self.fields['dealer'].queryset = Dealer.objects.all()