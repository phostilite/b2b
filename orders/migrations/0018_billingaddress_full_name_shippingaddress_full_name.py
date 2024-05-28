# Generated by Django 5.0.4 on 2024-05-26 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0017_orderitem_total_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='billingaddress',
            name='full_name',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='full_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]