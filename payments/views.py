from django.shortcuts import redirect, render
from .models import Payment
from orders.models import Order
import razorpay
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseServerError
from django.core import serializers
from django.http import JsonResponse
import json


client = razorpay.Client(auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))

import logging

logger = logging.getLogger(__name__)

def create_payment(order_id):
    logger.info(f"Creating payment for order {order_id}")
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order with id {order_id} does not exist.")
        return None

    amount = int(order.grand_total_amount * 100)  
    logger.info(f"Order amount: {amount}")

    data = {
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1'
    }

    try:
        response = client.order.create(data=data)
    except Exception as e:
        logger.error(f"Failed to create order with Razorpay: {e}")
        return None

    logger.info(f"Razorpay order created with id {response['id']}")
    return response['id'], order

def payment_view(request, order_id):
    logger.info(f"Processing payment view for order {order_id}")
    razorpay_order_id, order = create_payment(order_id)
    if razorpay_order_id is None:
        logger.error("Failed to create payment")
        return redirect('error_page')  

    amount = int(order.grand_total_amount * 100)  

    try:
        billing_address = order.billing_addresses.first() 
        if billing_address is None:
            raise ValueError("No billing address associated with this order.")
    except ValueError as e:
        logger.error(f"Failed to get billing address: {e}")
        return redirect('error_page')

    context = {
        'order_id': order_id,  
        'razorpay_order_id': razorpay_order_id,  
        'amount': amount,
        'billing_address': billing_address,
    }
    logger.info(f"Rendering payment page with context {context}")
    return render(request, 'dealer/payment.html', context)

def payment_success_view(request):
    logger.info(f"Received POST data: {request.POST}")
    
    logger.info("Processing payment success view")
    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    signature = request.POST.get('signature')

    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': signature
    }

    logger.info(f"Received payment details: {params_dict}")

    order_id = request.session.get('order_id')
    order = Order.objects.filter(id=order_id).first()
    if not order:
        logger.error(f"Order with id {order_id} does not exist.")
        return render(request, 'dealer/error.html')

    try:
        client.utility.verify_payment_signature(params_dict)
        logger.info("Payment signature verification successful")
        payment = Payment.objects.create(
            order=order, 
            payment_id=razorpay_payment_id, 
            razorpay_order_id=razorpay_order_id, 
            amount=order.grand_total_amount,
            status='Paid'
        )
        order.payment_status = 'Paid'  
        order.save()
        context = {'payment': payment}
        logger.info(f"Rendering payment success page with context {context}")
        return render(request, 'dealer/payment_success.html', context)
    except razorpay.errors.SignatureVerificationError as e:
        logger.error("Payment signature verification failed")
        payment = Payment.objects.create(
            order=order, 
            payment_id=razorpay_payment_id, 
            razorpay_order_id=razorpay_order_id, 
            amount=order.grand_total_amount,
            status='Failed',
            error_message=str(e)
        )
        order.payment_status = 'Failed'  
        order.save()
        return render(request, 'dealer/payment_failure.html')
    
def error_page_view(request):
    logger.info("Rendering error page")
    return render(request, 'dealer/error.html')