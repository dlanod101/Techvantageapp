from rest_framework import serializers
from .models import Post, UploadedFile, Comment
from users.models import CustomUser

class UploadedFileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    class Meta:
        model = UploadedFile
        fields = ['file_name', 'file_url', 'uploaded_at']  # Customize fields as needed

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    class Meta:
        model = Comment
        fields = ["user", "content", "date_published"]

    def get_user(self, obj):
        return obj.user.display_name  # Return the username, or you can return email, etc.

    
class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    files = UploadedFileSerializer(many=True, read_only=True)
    comments=CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ['user', 'content', 'color_code', 'date_published', 'files', 'comments']

    def get_user(self, obj):
        return obj.user.display_name  # Return the username, or you can return email, etc.
