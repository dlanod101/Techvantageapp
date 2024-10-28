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

class Friend(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="friend")
    profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="friends")
    is_friend = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.display_name} is friends with {self.profile.user.display_name}" if self.is_friend else "Not friends"