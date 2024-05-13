from rest_framework import serializers
from rest_framework import generics, permissions

from django.contrib.auth.models import User, Group

from orders.models import Order, OrderItem


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