# Standard library imports
from datetime import datetime
import logging
from decimal import Decimal

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
import requests
import traceback

# Local application/library specific imports
from accounts.decorators import allowed_users
from .models import Payment, Order, LineItem
from django_renderpdf.views import PDFView
from .utils import convert_amount_to_words

logger = logging.getLogger(__name__)


def filter_transactions(data):
    filtered_transactions = []
    for transaction in data['items']:
        if isinstance(transaction.get('notes'), dict) and \
           'woocommerce_order_id' in transaction['notes'] and \
           'woocommerce_order_number' in transaction['notes']:
            filtered_transactions.append(transaction)
    return filtered_transactions

def get_order_details(order_id):
    try:
        url = f"https://www.paroshiltex.com/wp-json/wc/v3/orders/{order_id}"
        response = requests.get(url, auth=(settings.WOOCOMMERCE_API_KEY, settings.WOOCOMMERCE_API_SECRET))
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        order_details = response.json()
        return order_details
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError) as e:
        # Handle exceptions related to the API request
        print(f"Error fetching order details: {e}")
        return None

@ratelimit(group='transactions_group', key='ip', block=True)
def transactions(request):
    try:
        logger.info('Starting transactions function')

        current_date = datetime.now()
        three_months_ago = current_date - relativedelta(months=4)
        current_timestamp = int(current_date.timestamp())
        three_months_ago_timestamp = int(three_months_ago.timestamp())
        url = f"https://api.razorpay.com/v1/payments?from={three_months_ago_timestamp}&to={current_timestamp}&count=100"
        
        logger.info('Sending request to Razorpay API')
        response = requests.get(url, auth=(settings.RAZORPAY_API_KEY, settings.RAZORPAY_API_SECRET))
        response.raise_for_status()  # Raise an exception for non-2xx status codes
        data = response.json()
        logger.info('Received response from Razorpay API')
        
        filtered_transactions = filter_transactions(data)
        logger.info(f'Filtered {len(filtered_transactions)} transactions')

        for transaction in filtered_transactions:
            order_id = transaction['notes']['woocommerce_order_id']
            order_details = get_order_details(order_id)
            if order_details:
                transaction['order_details'] = order_details

                logger.info(f'Creating payment for transaction {transaction["id"]}')
                payment, created = Payment.objects.get_or_create(
                    payment_id=transaction['id'],
                    defaults={
                        'amount': int(transaction['amount']) / 100,
                        'currency': transaction['currency'],
                        'status': transaction['status'],
                        'order_id': transaction['order_id'],
                        'method': transaction['method'],
                        'captured': transaction['captured'],
                        'description': transaction['description'],
                        'vpa': transaction['vpa'],
                        'email': transaction['email'],
                        'contact': transaction['contact'],
                        'fee': transaction['fee'],
                        'created_at': datetime.fromtimestamp(transaction['created_at']),
                        'acquirer_data': transaction['acquirer_data'],
                        'upi_details': transaction['upi'],
                    }
                )

                if created:
                    logger.info(f'Created payment for transaction {transaction["id"]}')
                    order_data = transaction['order_details']
                    order = Order.objects.create(
                        payment=payment,
                        order_id=order_data['id'],
                        status=order_data['status'],
                        currency=order_data['currency'],
                        total=order_data['total'],
                        customer_id=order_data['customer_id'],
                        order_key=order_data['order_key'],
                        billing_details=order_data['billing'],
                        shipping_details=order_data['shipping'],
                        payment_method=order_data['payment_method'],
                        transaction_id=order_data['transaction_id'],
                        customer_ip_address=order_data['customer_ip_address'],
                        customer_user_agent=order_data['customer_user_agent'],
                        created_via=order_data['created_via'],
                        date_created=order_data['date_created'],
                        date_modified=order_data['date_modified'],
                        date_paid=order_data['date_paid'] if order_data['date_paid'] else None,
                        cart_hash=order_data['cart_hash'],
                        order_number=order_data['number'],
                        meta_data=order_data['meta_data'],
                    )

                    logger.info(f'Created order for transaction {transaction["id"]}')
                    
                    for line_item_data in order_data['line_items']:
                        line_item = LineItem.objects.create(
                            order=order,
                            line_item_id=line_item_data['id'],
                            name=line_item_data['name'],
                            product_id=line_item_data['product_id'],
                            variation_id=line_item_data['variation_id'] if line_item_data['variation_id'] else None,
                            quantity=line_item_data['quantity'],
                            subtotal=line_item_data['subtotal'],
                            total=line_item_data['total'],
                            sku=line_item_data['sku'] if line_item_data['sku'] else '',
                            price=line_item_data['price'],
                            image_data=line_item_data['image'],
                            meta_data=line_item_data['meta_data'],
                        )
                        line_item.calculate_taxes()
                        
                    logger.info(f'Created line items for transaction {transaction["id"]}')


        return HttpResponse(status=204)

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching transactions: {e}")
        return JsonResponse({'error': str(e)}, status=500)

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
    
     # Calculate subtotal
    subtotal = sum([item.price * item.quantity for item in line_items])
    
    # Calculate total tax
    total_tax = order.total - subtotal
    
    context = {
        'order': order,
        'line_items': line_items,
        'subtotal': subtotal,
        'total_tax': total_tax,
        'total_in_words': convert_amount_to_words(order.total),
    }

    return render(request, 'invoiceapi/invoice.html', context)

@method_decorator(login_required, name='dispatch')
@method_decorator(allowed_users(allowed_roles=["Admin"]), name='dispatch')
class DownloadInvoicePDFView(PDFView):
    template_name = 'invoiceapi/invoice.html'
    base_url = None 

    def get_filename(self):
        order_id = self.kwargs.get('order_id')
        return f'invoice_{order_id}.pdf'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, order_id=order_id)
        line_items = order.line_items.all()

        # Calculate subtotal
        subtotal = sum([item.price * item.quantity for item in line_items])
        
        # Calculate total tax
        total_tax = order.total - subtotal


        context.update({  # Update context with all necessary variables
            'order': order,
            'line_items': line_items,
            'subtotal': subtotal,
            'total_tax': total_tax,
            'total_in_words': convert_amount_to_words(order.total),
        })
        return context
   
def download_invoice(request, order_id):
    # Since context is assembled within the PDFView, we don't need to do it here.

    # Render the PDF Template
    html = render_to_string('invoiceapi/invoice.html')  

    # Create PDFView object 
    pdf_view = DownloadInvoicePDFView.as_view(base_url=request.build_absolute_uri()) 

    # Generate the PDF response
    response = pdf_view(request, order_id=order_id) 

    return response