# Generated by Django 5.0.4 on 2024-05-27 16:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0011_dealer_otp_hash'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dealer',
            name='otp_hash',
        ),
    ]