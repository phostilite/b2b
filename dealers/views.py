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
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.forms import formset_factory
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

from .models import Dealer, Document
from orders.models import Order
from payments.models import Payment
from .forms import DealerForm, DealerProfileForm, DocumentForm
from accounts.decorators import allowed_users
from django.http import JsonResponse
from datetime import datetime, timedelta
from .utils import send_otp, verify_otp  # You need to implement these functions


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
    try:
        if request.user.is_authenticated:
            try:
                dealer = Dealer.objects.get(user=request.user)
                if dealer.agreement_accepted:
                    return redirect('dealer_dashboard')
            except Dealer.DoesNotExist:
                logger.error('Dealer object does not exist for the authenticated user.')
                
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                try:
                    dealer = Dealer.objects.get(user=user)
                    if dealer.agreement_accepted:  
                        return redirect('dealer_dashboard')  
                    else:
                        return redirect('agreement_view')  
                except ObjectDoesNotExist:
                    logger.error('Dealer object does not exist for the authenticated user.')
            else:
                messages.error(request, 'Invalid username or password.')
        return render(request, 'authentication/dealer_login.html')
    except Exception as e:
        logger.error(f'An error occurred in dealer_login_view: {e}')
        return render(request, 'authentication/dealer_login.html')  

# @csrf_exempt
# def agreement_view(request):
#     try:
#         if request.method == 'POST':
#             agreement = request.POST.get('agreement')
#             if agreement == 'accept':
#                 dealer = Dealer.objects.get(user=request.user)
#                 dealer.agreement_accepted = True
#                 dealer.save()
#                 return redirect('dealer_dashboard')  
#             elif agreement == 'decline':
#                 logout(request)
#                 return redirect('dealer_login')  
#             else:
#                 messages.error(request, 'Invalid agreement option.')
#         return render(request, 'dealer/agreement.html')
#     except Exception as e:
#         logger.error(f'An error occurred in agreement_view: {e}')
#         return render(request, 'dealer/agreement.html')  

@csrf_exempt
def agreement_view(request):
    if request.method == 'POST':
        agreement = request.POST.get('agreement')
        if agreement == 'accept':
            dealer = Dealer.objects.get(user=request.user)
            dealer.agreement_accepted = True
            dealer.save()
            return redirect('document_upload')
    return render(request, 'dealer/agreement_presentation.html')

def upload_documents(request):
    DocumentFormSet = formset_factory(DocumentForm, extra=0, min_num=1) 
    if request.method == 'POST':
        formset = DocumentFormSet(request.POST, request.FILES)
        
        if formset.is_valid():
            dealer = request.user.dealer

            for form in formset:
                file = form.cleaned_data.get('file')
                document_type = form.cleaned_data.get('document_type')

                if file and document_type:
                    document = Document(
                        dealer=dealer,
                        document_type=document_type,
                        file=file,
                    )
                    document.save()
                    logger.info(f'Document of type {document_type} uploaded for dealer {dealer.id}')

            # After saving all documents, redirect or display a success message
            return redirect('esignature_view')  # Replace with the actual URL

    else:
        formset = DocumentFormSet()

    return render(request, 'dealer/document_upload.html', {'formset': formset})


def esignature_view(request):
    if request.method == 'POST':
        if request.POST.get('agree_to_terms'):
            dealer = request.user.dealer
            # Mark the agreement as signed in your Dealer model
            dealer.agreement_signed = True
            dealer.save()
            logger.info(f'Agreement signed by dealer {dealer.id}')
            # Redirect to the dealer's dashboard or another appropriate page
            return redirect('dealer_dashboard')
    return render(request, 'dealer/esignature.html')

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
    

@require_POST
@login_required
def delete_dealer_view(request, dealer_id):
    try:
        dealer = get_object_or_404(Dealer, pk=dealer_id)
        user = dealer.user
        dealer.delete()
        user.delete()
        logger.info('Dealer with id %s and associated user deleted successfully', dealer_id)
        return JsonResponse({'status': 'success', 'message': 'Dealer and associated user deleted successfully'})
    except Exception as e:
        logger.error('An error occurred while deleting the dealer with id %s and associated user: %s', dealer_id, str(e))
        return HttpResponseServerError({'status': 'error', 'message': 'An error occurred while deleting the dealer and associated user: ' + str(e)})