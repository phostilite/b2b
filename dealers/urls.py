from django.urls import path

from . import views
from retailers import views as retailer_views
from orders import views as order_views
from stock import views as stock_views
from cart import views as cart_views
from payments import views as payment_views

urlpatterns = [
    path('login/', views.dealer_login_view, name='dealer_login'),
    path('logout/', views.dealer_logout_view, name='dealer_logout'),
    path('dashboard/', views.dealer_dashboard_view, name='dealer_dashboard'),
    path('create-retailer/', retailer_views.create_retailer, name='dealer_create_retailer'),
    path('retailer-list/', retailer_views.retailer_list_view, name='dealer_retailer_list'),
    path('order-list/', order_views.order_list_view, name='dealer_order_list'),
    path('product-list/', stock_views.product_list_view, name='dealer_product_list'),
    path('add_to_cart/', cart_views.add_to_cart, name='add_to_cart'),
    path('cart/', cart_views.view_cart, name='view_cart'),
    path('cart/<int:product_id>/', cart_views.delete_from_cart, name='delete_from_cart'),
    path('cart/<int:product_id>/<int:size_group_id>/', cart_views.delete_from_cart, name='delete_from_cart_with_size_group'),
    path('create-order/', order_views.create_order, name='create_order'),
    
    
    path('create_payment/<int:order_id>/', payment_views.create_payment, name='create_payment'),
    path('payment_view/<int:order_id>/', payment_views.payment_view, name='payment_view'),

    path('payment_processing/', payment_views.payment_processing_view, name='payment_processing'),
    path('payment_success/<str:payment_id>/', payment_views.payment_success, name='payment_success'),

    path('payment/error/', payment_views.error_page_view, name='error_page'),
    
    path('profile/', views.update_profile, name='dealer_profile'),
]