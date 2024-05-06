from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group
from django.utils import timezone
from django.conf import settings
from django.db.models import Sum

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token
from rest_framework import serializers
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from orders.models import Order

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['name']

class UserListSerializer(serializers.ModelSerializer):
    groups = GroupSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'groups']

class UserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

class IsAdminGroupUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user:
            return request.user.groups.filter(name='Admin').exists()
        return False

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