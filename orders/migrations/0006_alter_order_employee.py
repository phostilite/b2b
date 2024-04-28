# Generated by Django 5.0.4 on 2024-04-25 09:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_razorpay_order_id'),
        ('sales', '0003_alter_employee_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='sales.employee'),
        ),
    ]
