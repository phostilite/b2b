from django.db import models
from django.contrib.auth.models import User
from stock.models import Product, SizeGroup  

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    product_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    product_price_by_size_group = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    size_groups = models.ManyToManyField(SizeGroup) 