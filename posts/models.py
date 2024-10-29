from django.db import models
from users.models import CustomUser


# Create your models here.
class Post(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='post')
    content = models.TextField()
    color_code = models.CharField(max_length=20, default="#33AFFF")
    date_published = models.DateTimeField(auto_now_add = True)
    

    def __str__(self):
        return self.content
    
class Likes(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="likes")
    likes = models.IntegerField(default=0)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_likes")

    def __str__(self):
        return self.likes

class Comment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="comment")
    content = models.CharField(max_length=255)
    date_published = models.DateTimeField(auto_now_add = True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_comment")

    def __str__(self):
        return self.content
    
    
class UploadedFile(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='upload_file')  # Reference to the user
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='for_post')  # Reference to the post
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()  # To store the file URL
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.file_url}"