# Generated by Django 4.2.16 on 2024-11-08 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_alter_friend_chat_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='current_position',
            field=models.CharField(default='Nothing For Now', max_length=50),
        ),
    ]