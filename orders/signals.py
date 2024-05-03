from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Order, OrderHistory

@receiver(post_save, sender=Order)
def create_order_history(sender, instance, created, **kwargs):
    if not created:  
        OrderHistory.objects.create(order=instance, modified_by=instance.modified_by)