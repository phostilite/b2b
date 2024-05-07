from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('create-token/', views.CreateTokenView.as_view(), name='create_token'),
    
    path('orders-summary/', views.orders_summary_api, name='orders_summary_api'),
    path('top-selling-products/', views.top_selling_products_api, name='top_selling_products_api'),
] 
