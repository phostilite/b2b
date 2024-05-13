from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum, Q, Prefetch, Count, Value
from django.db.models.functions import TruncMonth, Coalesce, TruncYear
from datetime import datetime
from django.db.models import DecimalField
from django.db.models.functions import ExtractYear, ExtractMonth

from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, permissions

from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from orders.models import Order, OrderItem, SalesData
from stock.models import Product, ProductImage
from .serializers import UserListSerializer, UserSerializer, GroupSerializer, IsAdminGroupUser
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [IsAdminGroupUser]

class CreateTokenView(generics.CreateAPIView):
    permission_classes = [IsAdminGroupUser]  
    serializer_class = UserSerializer  
    
    def get(self, request, *args, **kwargs):
        return Response({'message': 'CreateTokenView is working'})

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'user_id is required'}, status=400)

        user = User.objects.get(id=user_id)  
        token, _ = GroupExpiringToken.objects.get_or_create(user=user)

        return Response({'token': token.key}) 

class GroupExpiringToken(Token):
    class Meta:
        proxy = True  

class GroupExpiringTokenAuthentication(TokenAuthentication):
    model = GroupExpiringToken

    def authenticate_credentials(self, key):
        try:
            token = self.model.objects.select_related('user').get(key=key)
        except self.model.DoesNotExist:
            raise AuthenticationFailed('Invalid token')

        if not token.user.is_active:
            raise AuthenticationFailed('User inactive or deleted')

        return (token.user, token)
       
class LineChartDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Get all years from SalesData with sales
        years_with_sales = (
            SalesData.objects.values_list('year', flat=True).distinct()
        )

        chart_data = {}
        for year in years_with_sales:
            # Get all months with sales for the given year
            months_with_sales = SalesData.objects.filter(year=year).order_by('month').values_list('month', flat=True)

            year_data = []
            for month in months_with_sales:
                month_data = SalesData.objects.get(year=year, month=month)
                year_data.append({
                    'month': month_data.month,
                    'sales_revenue': month_data.sales_revenue,
                    'orders_received': month_data.orders_received,
                    'orders_processed': month_data.orders_processed,
                    'orders_delivered': month_data.orders_delivered
                })

            # Fill in any missing months with zeros
            all_months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            for month in all_months:
                if month not in months_with_sales:
                    year_data.append({
                        'month': month,
                        'sales_revenue': 0,
                        'orders_received': 0,
                        'orders_processed': 0,
                        'orders_delivered': 0
                    })

            # Sort year_data by month
            year_data = sorted(year_data, key=lambda x: all_months.index(x['month']))

            # Calculate the total for each metric for the year
            total_data = {
                'month': 'Total',
                'sales_revenue': sum(item['sales_revenue'] for item in year_data),
                'orders_received': sum(item['orders_received'] for item in year_data),
                'orders_processed': sum(item['orders_processed'] for item in year_data),
                'orders_delivered': sum(item['orders_delivered'] for item in year_data),
            }

            # Create nested dictionary for each year
            chart_data[year] = {
                'monthly_data': year_data,
                'total_data': total_data
            }

        return Response(chart_data)
    
class YearlyUserTypeSalesView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sales_data = {}
        month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

        for user_type in ['dealer', 'employee']:
            if user_type == 'dealer':
                orders = Order.objects.filter(created_by__dealer__isnull=False, payment_status='Paid')
            else:  # user_type == 'employee'
                orders = Order.objects.filter(created_by__employee__isnull=False, payment_status='Paid')

            yearly_data = orders.annotate(year=ExtractYear('order_date')).values('year').annotate(total_sales=Sum('grand_total_amount')).order_by('year')

            for data in yearly_data:
                year = data['year']
                if year not in sales_data:
                    # Initialize sales_data[year] with dictionaries for both user types
                    sales_data[year] = {
                        'dealer': {
                            'monthly_data': [{'month': month, 'monthly_sales': 0.0, 'order_count': 0} for month in month_names],
                            'total_data': {'month': 'Total', 'sales_revenue': 0.0, 'total_order_count': 0},
                        },
                        'employee': {
                            'monthly_data': [{'month': month, 'monthly_sales': 0.0, 'order_count': 0} for month in month_names],
                            'total_data': {'month': 'Total', 'sales_revenue': 0.0, 'total_order_count': 0},
                        },
                    }

                # Initialize monthly_data with a list of dictionaries for all months
                monthly_data = sales_data[year][user_type]['monthly_data']

                actual_monthly_data = orders.filter(order_date__year=year).annotate(month=ExtractMonth('order_date')).values('month').annotate(monthly_sales=Sum('grand_total_amount'), order_count=Count('id')).order_by('month')

                # Update the dictionaries for the months that have data
                for month_data in actual_monthly_data:
                    month_index = month_data['month'] - 1
                    monthly_data[month_index]['monthly_sales'] = month_data['monthly_sales']
                    monthly_data[month_index]['order_count'] = month_data['order_count']

                total_order_count = orders.filter(order_date__year=year).count()

                sales_data[year][user_type]['total_data'] = {
                    'month': 'Total',
                    'sales_revenue': data['total_sales'],
                    'total_order_count': total_order_count,
                }

        return Response(sales_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_summary_api(request):
    total_count = Order.objects.count()
    today = timezone.now().date()
    todays_count = Order.objects.filter(order_date__date=today).count()
    total_sales = Order.objects.filter(payment_status='Paid').aggregate(total_sales=Sum('grand_total_amount'))['total_sales']
    if total_sales is None:
        total_sales = 0
        
    pending_orders = Order.objects.filter(status='Pending Approval').count()
    approved_orders = Order.objects.filter(status='Approved').count()
    canceled_orders = Order.objects.filter(status='Canceled').count()

    data = {
        'total_orders': total_count,
        'todays_orders': todays_count,
        'total_sales': total_sales,
        'pending_orders': pending_orders,
        'approved_orders': approved_orders,
        'canceled_orders': canceled_orders
    }
    return JsonResponse(data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_selling_products_api(request):
    top_selling_products = Product.objects.annotate(
        sales_count=Sum('orderitem__quantity', filter=Q(orderitem__order__payment_status='Paid'))
    ).order_by('-sales_count')[:5].prefetch_related(
        Prefetch('images', queryset=ProductImage.objects.filter(is_primary=True), to_attr='primary_images')
    )

    data = [
        {
            'id': product.id,
            'name': product.title,
            'sales_count': product.sales_count,
            'image_url': product.primary_images[0].image.url if product.primary_images else None,
        }
        for product in top_selling_products
    ]

    return JsonResponse(data, safe=False)

@api_view(['GET'])
def category_sales_api(request):
    category_sales = OrderItem.objects.values('product__type').annotate(total_sales=Sum('quantity'),total_revenue=Sum('order__grand_total_amount')).order_by('-total_sales')

    categories = []
    for category in category_sales:
        category_name = category['product__type']
        category_sales_count = category['total_sales']
        category_revenue = category['total_revenue']
        categories.append({
            'name': get_category_display(category_name),
            'sales': category_sales_count,
            'revenue': category_revenue
        })

    total_sales = sum(category['sales'] for category in categories)
    total_revenue = sum(category['revenue'] for category in categories)

    data = {
        'categories': categories,
        'total_sales': total_sales,
        'total_revenue': total_revenue
    }
    return Response(data)

def get_category_display(category_name):
    for choice in Product.PRODUCT_TYPES:
        if choice[0] == category_name:
            return choice[1]
    return category_name