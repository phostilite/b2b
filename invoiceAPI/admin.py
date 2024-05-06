from django.contrib import admin

from .models  import Payment, Order, LineItem, Invoice

admin.site.register(Payment)
admin.site.register(Order)
admin.site.register(LineItem)
admin.site.register(Invoice)