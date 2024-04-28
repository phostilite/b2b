from django.contrib import admin

from .models import Order, OrderItem, OrderHistory, BillingAddress, ShippingAddress

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderHistory)
admin.site.register(BillingAddress)
admin.site.register(ShippingAddress)