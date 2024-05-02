from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from .models import Dealer

class DealerForm(forms.ModelForm):
    username = forms.CharField(max_length=150)
    password1 = forms.CharField(widget=forms.PasswordInput, label='Password')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')

    class Meta:
        model = Dealer
        fields = ['first_name', 'last_name', 'phone', 'email', 'profile_pic']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('Username already exists.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')
            
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            email=self.cleaned_data['email']
        )
        dealer = super().save(commit=False)
        dealer.user = user
        if commit:
            dealer.save()
            group, created = Group.objects.get_or_create(name='Dealer')
            group.user_set.add(user)
        return dealer
    

class DealerProfileForm(forms.ModelForm):
    class Meta:
        model = Dealer
        fields = ['first_name', 'last_name', 'phone', 'email']