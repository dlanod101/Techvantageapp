from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file  # Firebase upload helper function
from .models import UserProfile, Experience, Education, Location, ProfilePicture
from .serializers import (
    UserProfileSerializer,
    ExperienceSerializer,
    EducationSerializer,
    LocationSerializer,
    ProfilePictureSerializer
)

from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import UserProfile

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


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
class ProfilePictureListCreateView(generics.ListCreateAPIView):
    serializer_class = ProfilePictureSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ProfilePicture.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user_profile = UserProfile.objects.get(user=self.request.user)
        uploaded_file = self.request.FILES.get('file')  # Retrieve uploaded file from request
        if uploaded_file:
            file_url = upload_app_file(uploaded_file, "User Profiles")  # Upload to Firebase and get URL
            serializer.save(user=self.request.user, profile=user_profile, file_url=file_url)
        else:
            raise ValueError("No file was uploaded.")


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