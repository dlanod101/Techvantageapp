# Generated by Django 4.2.16 on 2024-10-15 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
