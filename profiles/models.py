import random
from django.db import models
from users.models import CustomUser

class Experience(models.Model):
    """Experience Model"""
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='experiences')
    position = models.CharField(max_length=255)
    employment_type = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    current_job = models.BooleanField(default=False)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # Allow for current job

    def __str__(self):
        return self.position


class Education(models.Model):
    """Education Model"""
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='educations')
    school = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.school


class Location(models.Model):
    """Location Model"""
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='locations')
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.city}, {self.country}"


class UserProfile(models.Model):
    """UserProfile Model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="profile_user")
    about = models.TextField(blank=True, default="Nothing For Now")
    skills = models.CharField(max_length=255, blank=True)
    interest = models.CharField(max_length=255, blank=True)
    date_published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.about


class ProfilePicture(models.Model):
    """Profile Picture Model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='profile_user_image')
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='profile_pictures')
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_url}"

class CoverPicture(models.Model):
    """Cover Picture Model"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cover_user_image')
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='cover_pictures')
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_url}"


class FriendRequest(models.Model):
    sender = models.ForeignKey(CustomUser, related_name="sent_requests", on_delete=models.CASCADE)
    receiver = models.ForeignKey(CustomUser, related_name="received_requests", on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('sent', 'Sent'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='sent')
    created_at = models.DateTimeField(auto_now_add=True)

class Friend(models.Model):
    user = models.ForeignKey(CustomUser, related_name="friends", on_delete=models.CASCADE)
    friend = models.ForeignKey(CustomUser, related_name="friend_of", on_delete=models.CASCADE)
    chat_id = models.CharField(max_length=6, unique=True)
    
    def generate_chat_id():
        """Generate a unique 6-digit chat ID"""
        return ''.join(str(random.randint(0, 9)) for _ in range(6))

    def save(self, *args, **kwargs):
        if not self.chat_id:
            self.chat_id = self.generate_chat_id()
        super().save(*args, **kwargs)
