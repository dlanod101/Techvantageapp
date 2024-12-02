from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    class Meta:
        model = Job
        fields = ["user", "title", "link", "description", "location", "date_published"]

    def get_user(self, obj):
        return obj.user.display_name  # Return the username, or you can return email, etc.
