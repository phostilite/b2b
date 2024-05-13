from django.core.management.base import BaseCommand
from orders.models import Order, SalesData
from django.db.models import Sum, Count
from datetime import datetime

class Command(BaseCommand):
    help = 'Fill SalesData with data from existing orders for a specific month'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int, help='The year of the month you want to fill data for')
        parser.add_argument('month', type=int, help='The month you want to fill data for')

    def handle(self, *args, **options):
        year = options['year']
        month = options['month']

        # Calculate the sales and order data for this month and year.
        orders_in_month = Order.objects.filter(order_date__year=year, order_date__month=month)
        sales_revenue = orders_in_month.aggregate(Sum('grand_total_amount'))['grand_total_amount__sum'] or 0
        orders_received = orders_in_month.count()
        orders_processed = orders_in_month.filter(is_approved=True).count()
        orders_delivered = orders_in_month.filter(payment_status='Paid').count()

        # Update or create the SalesData record.
        SalesData.objects.update_or_create(
            year=year,
            month=datetime(year, month, 1).strftime('%B'),
            defaults={
                'sales_revenue': sales_revenue,
                'orders_received': orders_received,
                'orders_processed': orders_processed,
                'orders_delivered': orders_delivered,
            }
        )

        self.stdout.write(self.style.SUCCESS(f'Successfully filled SalesData for {datetime(year, month, 1).strftime("%B %Y")}'))