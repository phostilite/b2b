# Generated by Django 5.0.4 on 2024-04-25 12:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_billingaddress_order_shippingaddress_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='razorpay_order_id',
        ),
    ]
