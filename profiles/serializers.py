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
    sender_profile_picture = serializers.SerializerMethodField()
    
    class Meta:
        model = FriendRequest
        fields = ['id', 'sender', 'sender_profile_picture', 'receiver', 'status', 'created_at']

    def get_sender(self, obj):
        return {
            "id": obj.sender.uid,  # Return the username, or you can return email, etc.
            "display_name": obj.sender.display_name
        }
    
    def get_sender_profile_picture(self, obj):
        # Assuming `obj.sender` has a `UserProfile` with a related `ProfilePicture`
        user_profile = obj.sender.profile_user.first()
        if user_profile:
            profile_picture = user_profile.profile_pictures.first()  # Get the first profile picture, if any
            return profile_picture.file_url if profile_picture else None
        return None
    
    def get_receiver(self, obj):
        return obj.receiver.display_name

class FriendSerializer(serializers.ModelSerializer):
    friend = serializers.SerializerMethodField()
    friend_name = serializers.CharField(source='friend.display_name')
    friend_uid = serializers.CharField(source='friend.uid')
    friend_profile_picture = serializers.SerializerMethodField()

    class Meta:
        model = Friend
        fields = ['friend', 'friend_uid', 'friend_name', 'friend_profile_picture', 'chat_id']

    def get_friend(self, obj):
        return obj.friend.uid
    
    def get_friend_profile_picture(self, obj):
        # Access the UserProfile, then the ProfilePicture from that UserProfile
        user_profile = obj.friend.profile_user.first()  # Get the associated UserProfile
        if user_profile:
            profile_picture = user_profile.profile_pictures.first()  # Get the first profile picture, if any
            return profile_picture.file_url if profile_picture else None
        return None