from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def landing_page(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        elif request.user.groups.filter(name='Dealer').exists():
            return redirect('dealer_dashboard')
    return redirect('dealer_login')