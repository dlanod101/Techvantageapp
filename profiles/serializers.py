from rest_framework import serializers
from .models import UserProfile, Experience, Education, Location, ProfilePicture, Friend, CoverPicture, FriendRequest, Friend

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

class CoverPictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverPicture
        fields = ['id', 'user', 'profile', 'file_name', 'file_url', 'uploaded_at']
        read_only_fields = ['user', 'profile', 'file_url', 'uploaded_at']  # file_url will be set on Firebase upload


class UserProfileSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()  # Add a method to customize user data
    experiences = ExperienceSerializer(many=True, read_only=True)  # Nested serializer
    educations = EducationSerializer(many=True, read_only=True)
    locations = LocationSerializer(many=True, read_only=True)
    profile_pictures = ProfilePictureSerializer(many=True, read_only=True)
    cover_pictures = CoverPictureSerializer(many=True, read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'about', 'skills', 'interest', 'date_published',
            'experiences', 'educations', 'locations', 'profile_pictures','cover_pictures'
        ]
        read_only_fields = ['user', 'date_published']

    def get_user(self, obj):
        return {
            "id": obj.user.uid,  # Return the username, or you can return email, etc.
            "display_name": obj.user.display_name
        }

# Serializer for FriendRequest
class FriendRequestSerializer(serializers.ModelSerializer):
    sender = serializers.SerializerMethodField()  # Add a method to customize user data
    receiver = serializers.SerializerMethodField()  # Add a method to customize user data
    
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'receiver', 'status', 'created_at']

    def get_sender(self, obj):
        return {
            "id": obj.sender.uid,  # Return the username, or you can return email, etc.
            "display_name": obj.sender.display_name
        }
    
    def get_receiver(self, obj):
        return obj.receiver.display_name
    
# # Serializer for Friend
# class FriendSerializer(serializers.ModelSerializer):
#     friend = serializers.SerializerMethodField()  # Add a method to customize user data
#     friend_uid = serializers.SerializerMethodField()
#     class Meta:
#         model = Friend
#         fields = ['friend', 'friend_uid', 'chat_id']

#     def get_friend(self, obj):
#         return obj.friend.display_name
    
#     def get_friend_uid(self, obj):
#         return obj.friend.uid

class FriendSerializer(serializers.ModelSerializer):
    friend_name = serializers.CharField(source='friend.display_name')
    friend_uid = serializers.CharField(source='friend.uid')

    class Meta:
        model = Friend
        fields = ['friend_uid', 'friend_name', 'chat_id']
