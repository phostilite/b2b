from django.urls import path

from . import views
from dealers import views as dealer_views
from sales import views as sales_views
from stock import views as stock_views
from retailers import views as retailer_views
from orders import views as order_views

urlpatterns = [
    path('login/', views.admin_login_view, name='admin_login'),
    path('logout/', views.admin_logout_view, name='admin_logout'),
    path('dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    
    path('dealers/', dealer_views.dealer_list_view, name='dealer_list'),
    path('employees/', sales_views.employee_list_view, name='employee_list'),
    path('retailers/', retailer_views.retailer_list_view, name='retailer_list'),
    
    path('products/', stock_views.product_list_view, name='product_list'),
    path('product/<int:pk>/', stock_views.product_detail_view, name='product_detail'),
    path('create-product/', stock_views.create_product, name='create_product'),
    path('product/update/<int:pk>/', stock_views.product_update_view, name='update_product'),
    path('product/delete/<int:product_id>/', stock_views.delete_product_view, name='delete_product'),
    path('products/<int:product_id>/delete-image/<int:image_id>/', stock_views.delete_product_image, name='delete_product_image'),
    path('products/<int:product_id>/upload-images/', stock_views.upload_product_images, name='upload_product_images'),
    
    path('create-dealer/', dealer_views.create_dealer, name='create_dealer'),
    path('dealer/delete/<int:dealer_id>/', dealer_views.delete_dealer_view, name='delete_dealer'),

    
    path('create-retailer/', retailer_views.create_retailer, name='create_retailer'),
    path('retailer/delete/<int:retailer_id>/', retailer_views.delete_retailer_view, name='delete_retailer'),
    
    path('create-employee/', sales_views.create_employee, name='create_employee'),
    
    path('order-list/', order_views.order_list_view, name='order_list'), 
    path('order/<int:order_id>/details/', order_views.order_details_view, name='order_details'),
    path('order/<int:order_id>/approve/', order_views.approve_order, name='approve_order'),

    path('profile/', views.update_profile, name='adminuser_profile'),
]