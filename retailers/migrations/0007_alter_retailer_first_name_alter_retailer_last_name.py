# Generated by Django 5.0.4 on 2024-05-26 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('retailers', '0006_retailer_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailer',
            name='first_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='retailer',
            name='last_name',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
