from django.urls import path

from . import views
from retailers import views as retailer_views
from dealers import views as dealer_views

urlpatterns = [
    path('login/', views.employee_login_view, name='employee_login'),
    path('logout/', views.employee_logout_view, name='employee_logout'),
    path('dashboard/', views.employee_dashboard_view, name='employee_dashboard'),
    
    path('dealer-list/', dealer_views.dealer_list_view, name='employee_dealer_list'),
    path('retailer-list/', retailer_views.retailer_list_view, name='employee_retailer_list'),
    
    path('create-dealer/', dealer_views.create_dealer, name='employee_create_dealer'),
    path('create-retailer/', retailer_views.create_retailer, name='employee_create_retailer'),
    
    path('profile/', views.update_profile, name='employee_profile'),
]