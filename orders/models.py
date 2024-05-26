from django.db import models
from django.db.models import Sum, Count

from administration.models import AdminUser
from retailers.models import Retailer
from sales.models import Employee
from dealers.models import Dealer
from stock.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('Draft', 'Draft'),
        ('Pending Approval', 'Pending Approval'),
        ('Approved', 'Approved'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
    )
    PAYMENT_STATUS_CHOICES = (
        ('Not Paid', 'Not Paid'),
        ('Paid', 'Paid'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed'),
    )
    
    dealer = models.ForeignKey(Dealer, on_delete=models.SET_NULL, null=True)
    retailer = models.ForeignKey(Retailer, on_delete=models.SET_NULL, null=True)
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    admin = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True)
    
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
        
    order_date = models.DateTimeField(auto_now_add=True)
    order_number = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
       
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    
    grand_total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    is_approved = models.BooleanField(default=False)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='Not Paid')

    
    def __str__(self):
        return self.order_number
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method.

        # Calculate the sales and order data for the month and year of this order.
        orders_in_month = Order.objects.filter(order_date__year=self.order_date.year, order_date__month=self.order_date.month)
        sales_revenue = orders_in_month.aggregate(Sum('grand_total_amount'))['grand_total_amount__sum'] or 0
        orders_received = orders_in_month.count()
        orders_processed = orders_in_month.filter(status='processed').count()
        orders_delivered = orders_in_month.filter(status='delivered').count()

        # Update or create the SalesData record.
        SalesData.objects.update_or_create(
            year=self.order_date.year,
            month=self.order_date.strftime('%B'),
            defaults={
                'sales_revenue': sales_revenue,
                'orders_received': orders_received,
                'orders_processed': orders_processed,
                'orders_delivered': orders_delivered,
            }
        )
    
    
class OrderItem(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    quantity = models.IntegerField()
    item_size_group = models.CharField(max_length=255, null=True, blank=True)  
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.product.title}"

class OrderHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.order.order_number} - {self.field_name} changed" 
    
class BillingAddress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='billing_addresses', null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=50, null=True, blank=True)
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, null=True, blank=True)
    postcode = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)

class ShippingAddress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='shipping_addresses', null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    full_name = models.CharField(max_length=100, blank=True)
    company = models.CharField(max_length=50, null=True, blank=True)
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, null=True, blank=True)
    postcode = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)  
    
    
class SalesData(models.Model):
    year = models.IntegerField()
    month = models.CharField(max_length=50)
    sales_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    orders_received = models.IntegerField()
    orders_processed = models.IntegerField()
    orders_delivered = models.IntegerField()

    class Meta:
        unique_together = ('year', 'month')