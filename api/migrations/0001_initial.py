# Generated by Django 5.0.4 on 2024-05-08 04:06

from django.db import migrations


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('authtoken', '0004_alter_tokenproxy_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupExpiringToken',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('authtoken.token',),
        ),
    ]
