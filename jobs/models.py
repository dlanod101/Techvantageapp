from django.db import models
from users.models import CustomUser

# Create your models here.
class Job(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='job')
    title = models.CharField(max_length=255)
    description = models.TextField()
    Location = models.CharField(max_length=255)
    date_published = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title