from django.db import models

class Payment(models.Model):
    payment_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3)
    status = models.CharField(max_length=20)
    order_id = models.CharField(max_length=100)
    method = models.CharField(max_length=20)
    captured = models.BooleanField()
    description = models.CharField(max_length=100)
    vpa = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField()
    acquirer_data = models.JSONField(null=True, blank=True)
    upi_details = models.JSONField(null=True, blank=True)
    
    def __str__(self):
        return self.payment_id
    
class Order(models.Model):
    order_id = models.IntegerField(unique=True)
    status = models.CharField(max_length=20)
    currency = models.CharField(max_length=3)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    customer_id = models.IntegerField()
    order_key = models.CharField(max_length=100)
    billing_details = models.JSONField()
    shipping_details = models.JSONField()
    payment_method = models.CharField(max_length=20)
    transaction_id = models.CharField(max_length=100)
    customer_ip_address = models.GenericIPAddressField()
    customer_user_agent = models.CharField(max_length=200)
    created_via = models.CharField(max_length=20)
    date_created = models.DateTimeField()
    date_modified = models.DateTimeField()
    date_paid = models.DateTimeField(null=True, blank=True)
    cart_hash = models.CharField(max_length=100)
    order_number = models.IntegerField()
    meta_data = models.JSONField()
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='orders')
    
    def __str__(self):
        return str(self.order_id)
    

class LineItem(models.Model):
    line_item_id = models.IntegerField()
    name = models.CharField(max_length=200)
    product_id = models.IntegerField()
    variation_id = models.IntegerField(null=True, blank=True)
    quantity = models.IntegerField()
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    sku = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_data = models.JSONField(null=True, blank=True)
    meta_data = models.JSONField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='line_items')
    
    def __str__(self):
        return str(self.line_item_id)