from celery import shared_task
from django.core.mail import EmailMessage
from django.conf import settings
import requests
import traceback
import logging
from decimal import Decimal
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from django.test.client import RequestFactory
from django.http import HttpResponse


from django_renderpdf.views import PDFView
from django.shortcuts import get_object_or_404

from .models import Payment, Order, LineItem, Invoice
from .utils import convert_amount_to_words  


# Create a mock request
factory = RequestFactory()
request = factory.get('/')

logger = logging.getLogger(__name__)



class DownloadInvoicePDFView(PDFView):
    template_name = 'invoiceapi/invoice.html'
    base_url = None
    
    def dispatch(self, request=None, *args, **kwargs):
        if request is None:
            # Handle the case when no request object is provided
            return self.render_to_response(self.get_context_data(*args, **kwargs))
        else:
            return super().dispatch(request, *args, **kwargs)

    def get_filename(self):
        order_id = self.kwargs.get('order_id')
        return f'invoice_{order_id}.pdf'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        order_id = self.kwargs.get('order_id')
        order = get_object_or_404(Order, order_id=order_id)
        line_items = order.line_items.all()
        invoice = Invoice.objects.get(order=order)

        # Calculate subtotal
        subtotal = sum([item.price * item.quantity for item in line_items])

        # Calculate total tax
        total_tax = order.total - subtotal

        context.update({
            'order': order,
            'line_items': line_items,
            'subtotal': subtotal,
            'total_tax': total_tax,
            'invoice_number': invoice.invoice_number,
            'total_in_words': convert_amount_to_words(order.total),
        })
        return context

    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response.render()
        return response.rendered_content

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
    
@shared_task
def process_new_payments():
    try:
        logger.info('Starting process_new_payments task')

        current_date = datetime.now(timezone.utc)  # Use UTC for consistency
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
            process_single_transaction(transaction)  # Break down the processing

    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching transactions: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}\n{traceback.format_exc()}")
        
        
@shared_task
def process_single_transaction(transaction):
    if Payment.objects.filter(payment_id=transaction['id']).exists():
        return  # Skip if already processed

    order_id = transaction['notes']['woocommerce_order_id']
    order_details = get_order_details(order_id)
    if order_details:
        transaction['order_details'] = order_details

        logger.info(f'Creating payment for transaction {transaction["id"]}')
        create_payment_and_order(transaction)  # Create database entries

        invoice = Invoice.objects.get(order__payment__payment_id=transaction['id'])
        if not invoice.invoice_sent:
            generate_and_send_invoice(invoice)
    else:
        logger.warning(f"Order details not found for transaction {transaction['id']}")
        
        
@shared_task
def create_payment_and_order(transaction):
    if Payment.objects.filter(payment_id=transaction['id']).exists():
        return  # Skip if already processed

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
            'fee': transaction['fee'] if transaction['fee'] else '',
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
        invoice = Invoice.objects.create(order=order)

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
            # line_item.calculate_taxes()
            line_item.calculate_taxes_and_save()

        logger.info(f'Created line items for transaction {transaction["id"]}')
    
    
@shared_task
def generate_and_send_invoice(invoice):
    pdf_view = DownloadInvoicePDFView.as_view()
    response = pdf_view(request, order_id=invoice.order.order_id)

    # Ensure the response is a HttpResponse object and has content
    if isinstance(response, HttpResponse) and response.content:
        pdf_content = response.content
    else:
        logger.error(f"Failed to generate PDF for order {invoice.order.order_id}")
        return

    email_subject = f"Invoice for Order #{invoice.order.order_id}"
    email_body = "Please find your attached invoice."
    email_from = settings.DEFAULT_FROM_EMAIL
    email_to = invoice.order.billing_details['email']

    email_message = EmailMessage(email_subject, email_body, email_from, [email_to])
    email_message.attach(f"invoice_{invoice.order.order_id}.pdf", pdf_content, 'application/pdf')

    try:
        email_message.send()
        invoice.invoice_sent = True
        invoice.save()
    except Exception as e:
        logger.error(f"Failed to send invoice email for order {invoice.order.order_id}: {e}")
