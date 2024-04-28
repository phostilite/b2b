from django import forms
from django.contrib.auth.models import User

from .models import AdminUser

class AdminUserProfileForm(forms.ModelForm):
    class Meta:
        model = AdminUser
        fields = ['first_name', 'last_name', 'phone', 'email']