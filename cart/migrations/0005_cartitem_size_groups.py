# Generated by Django 3.1.7 on 2024-04-24 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0005_auto_20240424_0630'),
        ('cart', '0004_auto_20240424_0644'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='size_groups',
            field=models.ManyToManyField(to='stock.SizeGroup'),
        ),
    ]