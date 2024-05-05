from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.transactions, name='payment_details'),
    path('payments/', views.payment_list, name='api_payment_list'),
    path('orders/', views.order_list, name='api_order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='api_order_detail'),
    path('invoice/<int:order_id>/', views.invoice, name='api_invoice'),
    path('download-invoice/<int:order_id>/', views.download_invoice, name='api_download_invoice'),
]