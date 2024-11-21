from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file  # Firebase upload helper function
from .models import UserProfile, Experience, Education, Location, ProfilePicture, Friend, CoverPicture
from .serializers import (
    UserProfileSerializer,
    ExperienceSerializer,
    EducationSerializer,
    LocationSerializer,
    ProfilePictureSerializer,
    FriendSerializer,
    CoverPictureSerializer
)

from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import UserProfile
import string
import random


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create the UserProfile instance for the new user
        user_profile = UserProfile.objects.create(user=instance)
        
        # Set the default profile picture URL
        default_file_url = "https://firebasestorage.googleapis.com/v0/b/newproject-7ad97.appspot.com/o/blue%20blank%20pfp%20icon%20%F0%9F%92%99.jpg?alt=media&token=f169e7d1-35b6-4ba5-bea4-ff09131936a4"  # Replace with your actual URL
        
        # Create a ProfilePicture instance with the default URL
        ProfilePicture.objects.create(
            user=instance,
            profile=user_profile,
            file_name="default-profile-picture.png",
            file_url=default_file_url
        )

         # Create a CoverPicture instance with the default URL
        CoverPicture.objects.create(
            user=instance,
            profile=user_profile,
            file_name="default-profile-picture.png",
            file_url=default_file_url
        )


# Experience Views
class ExperienceListCreateView(generics.ListCreateAPIView):
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Experience.objects.filter(user_profile__user=self.request.user)

    def perform_create(self, serializer):
        user_profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(user_profile=user_profile)


# Education Views
class EducationListCreateView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(user_profile__user=self.request.user)

    def perform_create(self, serializer):
        user_profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(user_profile=user_profile)


# Location Views
class LocationListCreateView(generics.ListCreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Location.objects.filter(user_profile__user=self.request.user)

    def perform_create(self, serializer):
        user_profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(user_profile=user_profile)


# ProfilePicture Views
class ProfilePictureUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfilePictureSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve or create a profile picture entry for the user if it doesn’t already exist
        user_profile = UserProfile.objects.get(user=self.request.user)
        profile_picture, created = ProfilePicture.objects.get_or_create(
            user=self.request.user, profile=user_profile
        )
        return profile_picture

    def update(self, request, *args, **kwargs):
        profile_picture = self.get_object()
        uploaded_file = request.FILES.get('file')  # Get uploaded file from request

        if uploaded_file:
            file_url = upload_app_file(uploaded_file, "User Profiles")  # Upload to Firebase and get the URL
            profile_picture.file_name = f"{request.user.display_name} Profile Picture"
            profile_picture.file_url = file_url  # Update file_url with the new one
            profile_picture.save()
            serializer = self.get_serializer(profile_picture)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "No file was uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

# CoverPicture Views
class CoverPictureUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = CoverPictureSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve or create a profile picture entry for the user if it doesn’t already exist
        user_profile = UserProfile.objects.get(user=self.request.user)
        cover_picture, created = CoverPicture.objects.get_or_create(
            user=self.request.user, profile=user_profile
        )
        return cover_picture

    def update(self, request, *args, **kwargs):
        cover_picture = self.get_object()
        uploaded_file = request.FILES.get('file')  # Get uploaded file from request

        if uploaded_file:
            file_url = upload_app_file(uploaded_file, "User Cover Pictures")  # Upload to Firebase and get the URL
            cover_picture.file_name = f"{request.user.display_name} Cover Picture"
            cover_picture.file_url = file_url  # Update file_url with the new one
            cover_picture.save()
            serializer = self.get_serializer(cover_picture)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "No file was uploaded."},
                status=status.HTTP_400_BAD_REQUEST
            )

# UserProfile Views
class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(user=self.request.user)

    def put(self, request, *args, **kwargs):
        response = super().put(request, *args, **kwargs)
        response.data["message"] = "UserProfile updated successfully!"
        return response

class GetProfiles(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

     def get_queryset(self):
         return UserProfile.objects.all()

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import FriendRequest, Friend, CustomUser
from .serializers import FriendRequestSerializer, FriendSerializer

# Send Friend Request
@api_view(['POST'])
def send_friend_request(request, receiver_uid):
    receiver = get_object_or_404(CustomUser, uid=receiver_uid)
    if receiver == request.user:
        return Response({"message": "You cannot send a friend request to yourself."}, status=status.HTTP_400_BAD_REQUEST)
    
    friend_request, created = FriendRequest.objects.get_or_create(sender=request.user, receiver=receiver)
    if created:
        return Response({"message": "Friend request sent"}, status=status.HTTP_201_CREATED)
    return Response({"message": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)

# List Friend Requests
@api_view(['GET'])
def list_friend_requests(request):
    received_requests = FriendRequest.objects.filter(receiver=request.user, status='sent')
    serializer = FriendRequestSerializer(received_requests, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

# Accept Friend Request
def generate_chat_id():
    """Generate a unique 6-digit chat ID."""
    return ''.join(random.choices(string.digits, k=6))


@api_view(['POST'])
def accept_friend_request(request, sender_uid):
    sender = get_object_or_404(CustomUser, uid=sender_uid)
    friend_request = get_object_or_404(FriendRequest, sender=sender, receiver=request.user, status='sent')
    friend_request.status = 'accepted'
    friend_request.save()

    # Create mutual Friend objects with unique chat ID
    chat_id = Friend.generate_chat_id()  # Call the method to generate a unique chat ID
    Friend.objects.create(user=request.user, friend=sender, chat_id=chat_id)
    Friend.objects.create(user=sender, friend=request.user, chat_id=chat_id)

    return Response({"message": "Friend request accepted"}, status=status.HTTP_200_OK)

@api_view(['GET'])
def list_friends(request):
    friends = Friend.objects.filter(user=request.user)
    
    serializer = FriendSerializer(friends, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

