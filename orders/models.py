from django.db import models

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
    
    
class OrderItem(models.Model):
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    
    quantity = models.IntegerField()
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
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
    company = models.CharField(max_length=50, null=True, blank=True)
    address_1 = models.CharField(max_length=50)
    address_2 = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50, null=True, blank=True)
    postcode = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    email = models.EmailField(null=True, blank=True)
    phone = models.CharField(max_length=50, null=True, blank=True)  