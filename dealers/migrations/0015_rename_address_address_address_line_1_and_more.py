# Generated by Django 5.0.4 on 2024-05-27 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0014_remove_dealer_first_name_remove_dealer_last_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='address',
            new_name='address_line_1',
        ),
        migrations.AddField(
            model_name='address',
            name='address_line_2',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
