from django import forms
from .models import Retailer

class RetailerForm(forms.ModelForm):
    class Meta:
        model = Retailer
        fields = ['full_name', 'address', 'pincode', 'contact_number', 'email', 'gstin']