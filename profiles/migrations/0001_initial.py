# Generated by Django 4.2.16 on 2024-10-27 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0008_uploadedfile'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about', models.TextField(blank=True, default='Nothing For Now')),
                ('skills', models.CharField(blank=True, max_length=255)),
                ('interest', models.CharField(blank=True, max_length=255)),
                ('date_published', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_user', to='users.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='ProfilePicture',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file_name', models.CharField(max_length=255)),
                ('file_url', models.URLField()),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_pictures', to='profiles.userprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile_user_image', to='users.customuser')),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=50)),
                ('city', models.CharField(max_length=50)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='profiles.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(max_length=255)),
                ('employment_type', models.CharField(max_length=255)),
                ('company', models.CharField(max_length=255)),
                ('current_job', models.BooleanField(default=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(blank=True, null=True)),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='experiences', to='profiles.userprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Education',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('school', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('user_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='educations', to='profiles.userprofile')),
            ],
        ),
    ]