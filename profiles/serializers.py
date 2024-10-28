from rest_framework import serializers
from .models import UserProfile, Experience, Education, Location, ProfilePicture, Friend

class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = ['id', 'user_profile', 'position', 'employment_type', 'company', 'current_job', 'start_date', 'end_date']
        read_only_fields = ['user_profile']  # UserProfile is inferred from the context


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = ['id', 'user_profile', 'school', 'start_date', 'end_date']
        read_only_fields = ['user_profile']


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'user_profile', 'country', 'city']
        read_only_fields = ['user_profile']


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfilePicture
        fields = ['id', 'user', 'profile', 'file_name', 'file_url', 'uploaded_at']
        read_only_fields = ['user', 'profile', 'file_url', 'uploaded_at']  # file_url will be set on Firebase upload


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    experiences = ExperienceSerializer(many=True, read_only=True)  # Nested serializer
    educations = EducationSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)
    profile_pictures = ProfilePictureSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'about', 'skills', 'interest', 'date_published',
            'experiences', 'educations', 'locations', 'profile_pictures'
        ]
        read_only_fields = ['user', 'date_published']

    def get_user(self, obj):
        return obj.user.display_name  # Return the username, or you can return email, etc.

class FriendSerializer(serializers.ModelSerializer):
    friend_username = serializers.CharField(source="profile.user.username", read_only=True)
    friend_display_name = serializers.CharField(source="profile.user.display_name", read_only=True)

    class Meta:
        model = Friend
        fields = ["id", "profile", "friend_username", "friend_display_name", "is_friend"]

    def create(self, validated_data):
        user = self.context['request'].user
        profile = validated_data.get("profile")
        is_friend = validated_data.get("is_friend", True)
        
        # Ensure the friend isn't already added
        if Friend.objects.filter(user=user, profile=profile).exists():
            raise serializers.ValidationError("This user is already a friend.")

        return Friend.objects.create(user=user, profile=profile, is_friend=is_friend)
