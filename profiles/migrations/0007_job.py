# Generated by Django 4.2.16 on 2024-11-29 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_userprofile_current_position'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('job_type', models.CharField(default='Full-Time Job', max_length=50)),
                ('availability', models.CharField(default='Available Now', max_length=50)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_job', to='profiles.userprofile')),
            ],
        ),
    ]