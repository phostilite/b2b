# Generated by Django 5.0.4 on 2024-05-26 11:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0003_alter_adminuser_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='adminuser',
            name='full_name',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]