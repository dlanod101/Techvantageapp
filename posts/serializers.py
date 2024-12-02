from rest_framework import serializers
from .models import Post, UploadedFile, Comment, Like
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

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['user', 'created_at']
    
class PostSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    files = UploadedFileSerializer(many=True, read_only=True)
    comments=CommentSerializer(many=True, read_only=True)
    likes = LikeSerializer(many=True, read_only=True)
    like_count = serializers.IntegerField(source='like_count', read_only=True)

    class Meta:
        model = Post
        fields = ['user', 'content', 'color_code', 'date_published', 'files', 'comments', "likes", "like_count"]

    def get_user(self, obj):
        return obj.user.display_name  # Return the username, or you can return email, etc.
    
    
