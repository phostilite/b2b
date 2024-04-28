# Generated by Django 5.0.4 on 2024-04-25 10:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_remove_order_billing_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingaddress',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='billing_addresses', to='orders.order'),
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='shipping_addresses', to='orders.order'),
        ),
    ]