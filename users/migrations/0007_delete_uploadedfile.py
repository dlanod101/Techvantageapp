# Generated by Django 4.2.16 on 2024-10-17 03:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_uploadedfile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UploadedFile',
        ),
    ]
