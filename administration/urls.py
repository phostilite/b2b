from django.urls import path

from . import views
from dealers import views as dealer_views
from sales import views as sales_views
from stock import views as stock_views
from retailers import views as retailer_views

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    path('dealers/', dealer_views.dealer_list_view, name='dealer_list'),
    path('employees/', sales_views.employee_list_view, name='employee_list'),
    path('retailers/', retailer_views.retailer_list_view, name='retailer_list'),
    path('products/', stock_views.product_list_view, name='product_list'),
    path('create-product/', stock_views.create_product, name='create_product'),
    path('create-dealer/', dealer_views.create_dealer, name='create_dealer'),
    path('create-retailer/', retailer_views.create_retailer, name='create_retailer'),
    path('create-employee/', sales_views.create_employee, name='create_employee'), 
    
    path('profile/', views.update_profile, name='adminuser_profile')
]