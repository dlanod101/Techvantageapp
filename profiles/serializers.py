from rest_framework import serializers
from .models import UserProfile, Experience, Education, Location, ProfilePicture

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
