# Generated by Django 5.0.4 on 2024-05-08 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoiceAPI', '0009_alter_lineitem_cgst_alter_lineitem_sgst'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineitem',
            name='base_price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
