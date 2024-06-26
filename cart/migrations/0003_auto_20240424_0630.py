# Generated by Django 3.1.7 on 2024-04-24 06:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0002_cartitem_price'),
    ]

    operations = [
        migrations.RenameField(
            model_name='cartitem',
            old_name='price',
            new_name='product_price',
        ),
        migrations.AddField(
            model_name='cartitem',
            name='product_price_by_size_group',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='cart',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='cartitem',
            name='id',
            field=models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
