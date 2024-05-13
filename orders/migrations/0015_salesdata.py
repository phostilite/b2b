# Generated by Django 5.0.4 on 2024-05-12 20:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0014_alter_orderitem_unit_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.CharField(max_length=50)),
                ('sales_revenue', models.DecimalField(decimal_places=2, max_digits=10)),
                ('orders_received', models.IntegerField()),
                ('orders_processed', models.IntegerField()),
                ('orders_delivered', models.IntegerField()),
            ],
            options={
                'unique_together': {('year', 'month')},
            },
        ),
    ]
