from django.contrib import admin

from .models import Order, OrderItem, OrderHistory, BillingAddress, ShippingAddress, SalesData

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderHistory)
admin.site.register(BillingAddress)
admin.site.register(ShippingAddress)
admin.site.register(SalesData)