# Generated by Django 5.0.4 on 2024-05-15 20:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dealers', '0005_alter_document_document_type'),
    ]

    operations = [
        migrations.RenameField(
            model_name='document',
            old_name='file',
            new_name='files',
        ),
    ]