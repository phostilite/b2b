# Generated by Django 5.0.4 on 2024-05-03 08:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0012_orderitem_item_size_orderitem_unit_price_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderitem',
            old_name='item_size',
            new_name='item_size_group',
        ),
    ]
