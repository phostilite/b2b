# Generated by Django 5.0.4 on 2024-05-26 14:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0004_adminuser_full_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adminuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='adminuser',
            name='last_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]