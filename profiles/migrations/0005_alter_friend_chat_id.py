# Generated by Django 4.2.16 on 2024-11-01 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_remove_friend_is_friend_remove_friend_profile_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friend',
            name='chat_id',
            field=models.CharField(max_length=6),
        ),
    ]