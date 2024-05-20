from django.urls import path

from . import views
from retailers import views as retailer_views
from dealers import views as dealer_views
from stock import views as stock_views
from cart import views as cart_views
from orders import views as order_views

urlpatterns = [
    path('login/', views.employee_login_view, name='employee_login'),
    path('logout/', views.employee_logout_view, name='employee_logout'),
    path('dashboard/', views.employee_dashboard_view, name='employee_dashboard'),
    
    path('dealer-list/', dealer_views.dealer_list_view, name='employee_dealer_list'),
    path('retailer-list/', retailer_views.retailer_list_view, name='employee_retailer_list'),
    
    path('create-dealer/', dealer_views.create_dealer, name='employee_create_dealer'),
    path('create-retailer/', retailer_views.create_retailer, name='employee_create_retailer'),
    
    path('add_to_cart/', cart_views.add_to_cart, name='employee_add_to_cart'),
    path('cart/', cart_views.view_cart, name='employee_view_cart'),
    path('cart/<int:product_id>/', cart_views.delete_from_cart, name='employee_delete_from_cart'),
    path('cart/<int:product_id>/<int:size_group_id>/', cart_views.delete_from_cart, name='employee_delete_from_cart_with_size_group'),
    path('create-order/', order_views.create_order, name='employee_create_order'),
    path('order-confirmation/', order_views.order_confirmation_view, name='employee_order_confirmation'),
    path('product-list/', stock_views.product_list_view, name='employee_product_list'),
    path('order-list/', order_views.order_list_view, name='employee_order_list'),

    
    
    path('profile/', views.update_profile, name='employee_profile'),
    
]