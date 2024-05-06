# Generated by Django 5.0.4 on 2024-05-05 21:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoiceAPI', '0006_lineitem_subtotal_2'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=100, unique=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='invoiceAPI.order')),
            ],
        ),
    ]