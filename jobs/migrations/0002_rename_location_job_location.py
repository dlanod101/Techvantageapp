# Generated by Django 4.2.16 on 2024-10-23 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='job',
            old_name='Location',
            new_name='location',
        ),
    ]
