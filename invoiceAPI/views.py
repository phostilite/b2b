# Standard library imports
from datetime import datetime
import logging
from decimal import Decimal
import json
import hmac

# Related third party imports
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt
import requests
import traceback

# Local application/library specific imports
from accounts.decorators import allowed_users
from .models import Payment, Order, LineItem, Invoice
from django_renderpdf.views import PDFView
from .tasks import process_new_payments, generate_and_send_invoice
from .utils import convert_amount_to_words

logger = logging.getLogger(__name__)

@ratelimit(group='transactions_group', key='ip', block=True)
def transactions(request):
    try:
        logger.info('Starting transactions function')
        process_new_payments.delay()  # Trigger the Celery task
        return HttpResponse(status=204)
    except Exception as e:
        logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

@login_required
@allowed_users(allowed_roles=["Admin"])   
def payment_list(request):
    payments = Payment.objects.all()
    context = {'payments': payments}
    return render(request, 'invoiceapi/payment_list.html', context)

@login_required
@allowed_users(allowed_roles=["Admin"]) 
def order_list(request):
    orders = Order.objects.all()
    context = {'orders': orders}
    return render(request, 'invoiceapi/order_list.html', context)

@login_required
@allowed_users(allowed_roles=["Admin"]) 
def order_detail(request, order_id):
    order = Order.objects.get(order_id=order_id)
    line_items = order.line_items.all()
    context = {'order': order, 'line_items': line_items}
    return render(request, 'invoiceapi/order_detail.html', context)

@login_required
@allowed_users(allowed_roles=["Admin"]) 
def invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    line_items = order.line_items.all()
    invoice = Invoice.objects.get(order=order)
    
     # Calculate subtotal
    subtotal = sum([item.price * item.quantity for item in line_items])
    
    # Calculate total tax
    total_tax = order.total - subtotal
    
    context = {
        'order': order,
        'line_items': line_items,
        'subtotal': subtotal,
        'total_tax': total_tax,
        'invoice_number': invoice.invoice_number,
        'total_in_words': convert_amount_to_words(order.total),
    }

    return render(request, 'invoiceapi/invoice.html', context)

@login_required
@allowed_users(allowed_roles=["Admin"])
def download_invoice(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    invoice = Invoice.objects.get(order=order)

    # if not invoice.invoice_sent:
        # generate_and_send_invoice.delay(invoice)

    return JsonResponse({'message': 'Invoice generation in progress'})

@csrf_exempt
def razorpay_webhook(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        event = payload.get('event')

        # Log the received event
        logger.info(f'Received event: {event}')

        # Signature Verification
        secret = settings.RAZORPAY_WEBHOOK_SECRET
        signature = request.headers.get('X-Razorpay-Signature')

        if signature:
            digest = hmac.new(secret.encode(), request.body, 'sha256').hexdigest()
            if not hmac.compare_digest(digest, signature):
                logger.warning('Invalid signature')
                return HttpResponse(status=400)  # Invalid signature

        # Process the payment event
        if event == 'payment.authorized': 
            logger.info('Processing new payments')
            process_new_payments.delay()  
        return HttpResponse(status=200)
    else:
        logger.warning('Received non-POST request')
        return HttpResponse(status=400)