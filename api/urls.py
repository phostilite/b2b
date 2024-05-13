from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.UserListView.as_view(), name='user-list'),
    path('create-token/', views.CreateTokenView.as_view(), name='create_token'),
    
    path('orders-summary/', views.orders_summary_api, name='orders_summary_api'),
    path('top-selling-products/', views.top_selling_products_api, name='top_selling_products_api'),
    path('category-sales/', views.category_sales_api, name='category_sales_api'),
    path('line-chart-data/', views.LineChartDataAPIView.as_view(), name='line-chart-data'),
    path('yearly_user_type_sales/', views.YearlyUserTypeSalesView.as_view(), name='yearly_user_type_sales'),
] 