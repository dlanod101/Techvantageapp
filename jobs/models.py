from django.db import models
from users.models import CustomUser

# Create your models here.
class Job(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job')
    title = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=False)
    link = models.URLField(blank=False)
    location = models.CharField(max_length=255, blank=False)
    date_published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class UploadedFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='upload_job_pic')  # Reference to the user
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='for_job')  # Reference to the post
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()  # To store the file URL
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_url}"