from rest_framework import serializers
from .models import Post, UploadedFile
from users.models import CustomUser

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ['file_name', 'file_url', 'uploaded_at']  # Customize fields as needed


class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    files = UploadedFileSerializer(many=True, read_only=True)


    class Meta:
        model = Post
        fields = ['user', 'content', 'color_code', 'date_published', 'files']

    def get_user(self, obj):
        return obj.user.display_name  # Return the username, or you can return email, etc.
