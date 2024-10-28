from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file  # Firebase upload helper function
from .models import UserProfile, Experience, Education, Location, ProfilePicture, Friend
from .serializers import (
    UserProfileSerializer,
    ExperienceSerializer,
    EducationSerializer,
    LocationSerializer,
    ProfilePictureSerializer,
    FriendSerializer
)

from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import UserProfile

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
            profile_picture.file_url = file_url  # Update file_url with the new one
            profile_picture.save()
            serializer = self.get_serializer(profile_picture)
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

class FriendListCreateView(generics.ListCreateAPIView):
    serializer_class = FriendSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Filter friends where the authenticated user is the main user and is_friend is True
        return Friend.objects.filter(user=self.request.user, is_friend=True)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(
            {"message": "Friend added successfully!", "friend": serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        # Set the current user as the 'user' for the new friend entry
        serializer.save(user=self.request.user)
