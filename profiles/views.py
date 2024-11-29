from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file  # Firebase upload helper function
from .models import UserProfile, Experience, Education, Location, ProfilePicture, Friend, CoverPicture
from rest_framework.views import APIView
from django.core.exceptions import ObjectDoesNotExist
from .serializers import (
    UserProfileSerializer,
    ExperienceSerializer,
    EducationSerializer,
    LocationSerializer,
    ProfilePictureSerializer,
    FriendSerializer,
    CoverPictureSerializer,
    #ApiResponseSerializer
)

from django.db.models.signals import post_save
from django.dispatch import receiver
from users.models import CustomUser
from .models import UserProfile
import string
import random
from django.db.models import Q

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

class ExperienceUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Experience.objects.all()
    serializer_class = ExperienceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Experience retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "message": "Experience updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Experience deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)


# Education Views
class EducationListCreateView(generics.ListCreateAPIView):
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(user_profile__user=self.request.user)

    def perform_create(self, serializer):
        user_profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(user_profile=user_profile)

class EducationUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Education retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "message": "Education updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Education deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)

# Location Views
class LocationListCreateView(generics.ListCreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Location.objects.filter(user_profile__user=self.request.user)

    def perform_create(self, serializer):
        user_profile = UserProfile.objects.get(user=self.request.user)
        serializer.save(user_profile=user_profile)

class LocationUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "message": "Location retrieved successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "message": "Location updated successfully.",
            "data": serializer.data
        }, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Location deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)



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

# UserProfile Views
class SpecificUserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            user = request.user
            profile =  UserProfile.objects.get(id=pk)
            profile_picture = profile.profile_pictures.first().file_url if profile.profile_pictures.exists() else None 
            cover_picture = profile.cover_pictures.first().file_url if profile.cover_pictures.exists() else None 

            experience_data = [{
                'id': exp.id,
                'position': exp.position,
                'employment_type': exp.employment_type,
                'company': exp.company,
                'current_job': exp.current_job,
                'start_date':exp.start_date,
                'end_date':exp.end_date,
                 } for exp in profile.experiences.all()
            ]

            education_data = [{
                'id': edu.id,
                'school': edu.school,
                'start_date': edu.start_date,
                'end_date': edu.end_date,
            } for edu in profile.educations.all()]

            location_data = [{
                'id':loc.id,
                'country': loc.country,
                'city': loc.city,
            } for loc in profile.locations.all()]

            response_data = {
                "id": profile.id,
                "user": profile.user.display_name,
                "user_id": profile.user.uid,
                "profile_picture": profile_picture,
                "cover_picture": cover_picture,
                "about": profile.about,
                'skills': profile.skills,
                'interest': profile.interest,
                'current_position': profile.current_position,
                'experience': experience_data,
                'education': education_data,
                'location': location_data,
                "is_friend": self.is_friend(user, profile.user),
                "is_friend_request_sent": self.is_friend_request_sent(user, profile.user)
                }
            return Response({"message": "Profile retrieved successfully.", "profile": response_data}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
    def is_friend(self, current_user, other_user):
        """Check if two users are friends."""
        return Friend.objects.filter(
            (Q(user=current_user) & Q(friend=other_user)) |
            (Q(user=other_user) & Q(friend=current_user))
        ).exists()
    
    def is_friend_request_sent(self, current_user, other_user):
        """Check if two users are friends."""
        return FriendRequest.objects.filter(
            (Q(sender=current_user) & Q(receiver=other_user)) |
            (Q(sender=other_user) & Q(receiver=current_user))
        ).exists()
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Prefetch

class ProfileFind(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Prefetch related profile pictures to minimize queries
        profiles = UserProfile.objects.exclude(user=user).prefetch_related(
            Prefetch('profile_pictures', to_attr='prefetched_pictures')
        )

        # Format the response data
        profiles_data = [
            {
                "id": profile.id,
                "user": profile.user.display_name,
                "user_id": profile.user.uid,
                "profile_picture": [
                    {"file_url": pic.file_url} for pic in profile.prefetched_pictures
                ],
                "about": profile.about,
                # Add other fields as needed
            }
            for profile in profiles
        ]

        return Response(profiles_data, status=status.HTTP_200_OK)

    
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

@swagger_auto_schema(
    method='get',
    responses={200: FriendRequestSerializer},
    operation_summary="List Friend Request",
    operation_description="Retrieve a list of all friend requests for the authenticated user."
)
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

@swagger_auto_schema(
    method='get',
    responses={200: FriendSerializer},
    operation_summary="List Friends",
    operation_description="Retrieve a list of all friends for the authenticated user."
)
@api_view(['GET'])
def list_friends(request):
    friends = Friend.objects.filter(user=request.user)
    
    serializer = FriendSerializer(friends, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

