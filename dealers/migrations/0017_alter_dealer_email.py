# Generated by Django 5.0.4 on 2024-05-28 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0016_address_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dealer',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, unique=True),
        ),
    ]
