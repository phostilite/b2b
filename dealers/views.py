import logging
import os
from datetime import datetime, timedelta
import tempfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import Group, User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Prefetch, Count, Sum
from django.db.models.functions import ExtractWeekDay
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.core.cache import cache
from django.forms import formset_factory
from django.http import Http404, JsonResponse, HttpResponseServerError, HttpResponse, HttpResponseRedirect, FileResponse
from django.views.decorators.http import require_POST
from django.template.loader import get_template, render_to_string
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings

from weasyprint import HTML

from .models import Dealer, Document
from orders.models import Order
from payments.models import Payment
from .forms import DealerForm, DealerProfileForm, DocumentForm, OTPForm, DealerAddressForm
from accounts.decorators import allowed_users
from .utils import send_otp, verify_otp, generate_otp

logger = logging.getLogger(__name__)


@login_required
@allowed_users(allowed_roles=["Dealer"])
def dealer_dashboard_view(request):
    dealer = Dealer.objects.get(user=request.user)
    orders = Order.objects.filter(dealer=dealer)
    payments = Payment.objects.filter(
        order__in=orders).order_by('-date_paid')[:10]

    total_orders = orders.count()

    pending_orders = orders.filter(status='Pending').count()
    approved_orders = orders.filter(status='Approved').count()
    delivered_orders = orders.filter(status='Delivered').count()

    pending_percentage = (pending_orders / total_orders) * \
        100 if total_orders else 0
    approved_percentage = (approved_orders / total_orders) * \
        100 if total_orders else 0
    delivered_percentage = (
        delivered_orders / total_orders) * 100 if total_orders else 0

    current_week = timezone.now().isocalendar().week
    orders_this_week = orders.filter(order_date__week=current_week)

    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    orders_data = [0] * 7
    amount_data = [0] * 7

    orders_by_day = orders_this_week.annotate(
        day_of_week=ExtractWeekDay('order_date')).values('day_of_week').annotate(
        count=Count('id'), total=Sum('grand_total_amount')).order_by('day_of_week')

    for order in orders_by_day:
        index = (order['day_of_week'] - 2) % 7
        orders_data[index] = order['count']
        amount_data[index] = float(order['total'])

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
    form_errors = []

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
                        request.session['dealer_id'] = dealer.id
                        return redirect('dealer_dashboard')
                    else:
                        return redirect('agreement_view')
                except ObjectDoesNotExist:
                    logger.error('Dealer object does not exist for the authenticated user.')
            else:
                form_errors.append('Username or Password: Invalid username or password.')
        return render(request, 'authentication/dealer_login.html', {'form_errors': form_errors})
    except Exception as e:
        logger.error(f'An error occurred in dealer_login_view: {e}')
        return render(request, 'authentication/dealer_login.html', {'form_errors': form_errors})


@csrf_exempt
def agreement_view(request):
    if request.method == 'POST':
        agreement = request.POST.get('agreement')
        if agreement == 'accept':
            dealer = Dealer.objects.get(user=request.user)
            dealer.agreement_accepted = True

            template = get_template('dealer/agreement_presentation.html')
            context = {'dealer': dealer}
            html_string = template.render(context)
            start_marker = '<!-- start_agreement_body -->'
            end_marker = '<!-- end_agreement_body -->'
            start_index = html_string.find(start_marker) + len(start_marker)
            end_index = html_string.find(end_marker)
            agreement_body = html_string[start_index:end_index]

            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                HTML(string=agreement_body).write_pdf(tmp.name)
                document = Document.objects.create(
                    dealer=dealer,
                    document_type='Agreement',
                    file=None
                )
                document.file.save(f'dealer_{dealer.id}_agreement.pdf', tmp.file)

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
                    logger.info(f'Document of type {document_type} uploaded for dealer { dealer.id}')

            return redirect('esignature_view')

    else:
        formset = DocumentFormSet()

    return render(request, 'dealer/document_upload.html', {'formset': formset})


@login_required
def esignature_view(request):
    form_errors = []

    if request.method == 'GET':
        otp = send_otp(request.user.dealer)
        request.session['otp'] = otp
        logger.info(f'OTP sent to dealer {request.user.dealer.id}: {otp}')
        messages.success(request, 'OTP has been sent to your email.')
        form = OTPForm()
        return render(request, 'dealer/esignature.html', {'form': form, 'messages': messages.get_messages(request)})

    if request.method == 'POST':
        form = OTPForm(request.POST)

        if form.is_valid():
            user_otp = form.cleaned_data.get('otp')
            session_otp = request.session.get('otp')
            logger.info(
                f'OTP received from dealer {request.user.dealer.id}: {user_otp}')

            if verify_otp(session_otp, user_otp):
                if request.POST.get('agree_to_terms'):
                    request.user.dealer.agreement_accepted = True
                    request.user.dealer.save()
                    logger.info(f'Agreement signed by dealer {request.user.dealer.id}')
                    messages.success(request, 'Agreement successfully signed.')
                    return redirect('dealer_dashboard')
                else:
                    messages.error(
                        request, 'Please agree to the terms and conditions.')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
                logger.warning(f'Invalid OTP entered by dealer {request.user.dealer.id}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    form_errors.append(f'{field.title()}: {error}')

        return render(request,
                      'dealer/esignature.html',
                      {'form': form,
                       'form_errors': form_errors,
                       'messages': messages.get_messages(request)})


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
    form_errors = []
    
    if request.method == 'POST':
        form = DealerForm(request.POST, request.FILES)
        address_form = DealerAddressForm(request.POST)

        if form.is_valid() and (not address_form.has_changed() or address_form.is_valid()):
            dealer = form.save()

            if address_form.has_changed() and address_form.is_valid():
                address = address_form.save(commit=False)
                address.dealer = dealer
                address.save()

            return redirect('dealer_list')
        else:
            logger.error(f'DealerForm errors: {form.errors}')
            logger.error(f'DealerAddressForm errors: {address_form.errors}')
            for field, errors in form.errors.items():
                for error in errors:
                    form_errors.append(f'{field.title()}: {error}')
    else:
        form = DealerForm()
        address_form = DealerAddressForm()

    if request.user.groups.filter(name='Admin').exists():
        return render(request, 'admin/create_dealer.html', {'form': form, 'address_form': address_form, 'form_errors': form_errors})
    elif request.user.groups.filter(name='Sales').exists():
        return render(request, 'employee/create_dealer.html', {'form': form, 'address_form': address_form, 'form_errors': form_errors})


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = DealerProfileForm(
            request.POST,
            request.FILES,
            instance=request.user.dealer)
        if form.is_valid():
            dealer = form.save(commit=False)
            dealer.user.first_name = dealer.full_name.split(' ')[0]
            dealer.user.last_name = dealer.full_name.split(' ')[1]
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


def get_dealer_data(request):
    dealer_id = request.session.get('dealer_id')
    dealer = get_object_or_404(Dealer, id=dealer_id)
    addresses = dealer.addresses.all()
    documents = dealer.documents.all()

    dealer_data = {
        'full_name': dealer.full_name,
        'phone': dealer.phone,
        'email': dealer.email,
        'agreement_accepted': dealer.agreement_accepted,
        'gstin': dealer.gstin,
        'addresses': [
            {
                'address_line_1': address.address_line_1,
                'address_line_2': address.address_line_2,
                'city': address.city,
                'state': address.state,
                'zip_code': address.zip_code,
                'country': address.country,
            }
            for address in addresses
        ],
    }
    return JsonResponse(dealer_data)


@login_required
def dealer_documents_list(request):
    dealer_id = request.session.get('dealer_id')
    dealer = get_object_or_404(Dealer, id=dealer_id)
    documents = dealer.documents.all()
    return render(request, 'dealer/documents_list.html', {'documents': documents})


@login_required
def delete_document(request, document_id):
    if request.method == 'DELETE':
        document = Document.objects.get(id=document_id)
        document.delete()
        return HttpResponse('Document deleted successfully')
    else:
        return HttpResponse('Invalid request method', status=405)


@login_required
def download_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)
    file_path = document.file.path

    if os.path.exists(file_path):
        file = open(file_path, 'rb')
        response = FileResponse(
            file,
            as_attachment=True,
            filename=os.path.basename(file_path))
        return response

    raise Http404
