import logging
from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Prefetch
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count, Sum
from django.db.models.functions import ExtractWeekDay

from .models import Dealer
from orders.models import Order
from payments.models import Payment
from .forms import DealerForm, DealerProfileForm
from accounts.decorators import allowed_users
from django.http import JsonResponse
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@login_required
@allowed_users(allowed_roles=["Dealer"])
def dealer_dashboard_view(request):
    dealer = Dealer.objects.get(user=request.user)
    orders = Order.objects.filter(dealer=dealer)
    payments = Payment.objects.filter(order__in=orders).order_by('-date_paid')[:10]
    
    total_orders = orders.count()
    
    pending_orders = orders.filter(status='Pending').count()
    approved_orders = orders.filter(status='Approved').count()
    delivered_orders = orders.filter(status='Delivered').count()
    
    pending_percentage = (pending_orders / total_orders) * 100 if total_orders else 0
    approved_percentage = (approved_orders / total_orders) * 100 if total_orders else 0
    delivered_percentage = (delivered_orders / total_orders) * 100 if total_orders else 0
    
    current_week = timezone.now().isocalendar().week
    orders_this_week = orders.filter(order_date__week=current_week)
    
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    orders_data = [0]*7
    amount_data = [0]*7
    
    orders_by_day = orders_this_week.annotate(day_of_week=ExtractWeekDay('order_date')).values('day_of_week').annotate(count=Count('id'), total=Sum('grand_total_amount')).order_by('day_of_week')

    for order in orders_by_day:
        # Django's ExtractWeekDay function returns 1 for Sunday, 2 for Monday, ..., 7 for Saturday
        # So we need to adjust the index to match our days_of_week list
        index = (order['day_of_week'] - 2) % 7
        orders_data[index] = order['count']
        amount_data[index] = float(order['total'])  # Changed 'total' to 'grand_total_amount'
    
    orders_this_week = orders_this_week.count()
    
    context = {
        'dealer': dealer,
        'orders': orders,
        'payments': payments,
        'pending_percentage': pending_percentage,
        'approved_percentage': approved_percentage,
        'delivered_percentage': delivered_percentage,
        'orders_data': orders_data,
        'amount_data': amount_data,
        'orders_this_week': orders_this_week,
    }
    return render(request, 'dealer/dashboard.html', context)
  

def dealer_login_view(request):
    if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dealer_dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'authentication/dealer_login.html')

def dealer_logout_view(request):
    logout(request)
    return redirect('dealer_login')

@login_required
@allowed_users(allowed_roles=["Admin", "Sales"])
def dealer_list_view(request):
    if request.user.groups.filter(name='Admin').exists():
        dealers = Dealer.objects.all()
        return render(request, 'admin/dealer_list.html', {'dealers': dealers})
    elif request.user.groups.filter(name='Sales').exists():
        dealers = Dealer.objects.all()
        return render(request, 'employee/dealer_list.html', {'dealers': dealers})

@login_required
@allowed_users(allowed_roles=["Admin", "Sales"])
def create_dealer(request):
    if request.method == 'POST':
        form = DealerForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('dealer_list')
        else:
            logger.error(f'DealerForm errors: {form.errors}')
    else:
        form = DealerForm()
        
    if request.user.groups.filter(name='Admin').exists():
        return render(request, 'admin/create_dealer.html', {'form': form})
    elif request.user.groups.filter(name='Sales').exists():
        return render(request, 'employee/create_dealer.html', {'form': form})
    
    

login_required
def update_profile(request):
    if request.method == 'POST':
        form = DealerProfileForm(request.POST, request.FILES, instance=request.user.dealer)
        if form.is_valid():
            dealer = form.save(commit=False)
            dealer.user.first_name = dealer.first_name
            dealer.user.last_name = dealer.last_name
            dealer.user.email = dealer.email
            dealer.user.save()
            dealer.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('dealer_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = DealerProfileForm(instance=request.user.dealer)
    return render(request, 'dealer/profile.html', {
        'form': form
    })