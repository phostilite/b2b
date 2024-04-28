from django.contrib import admin

from .models import Product, ProductImage, Size, SizeGroup, Color

admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(Size)
admin.site.register(SizeGroup)
admin.site.register(Color)
