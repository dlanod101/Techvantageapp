from django.shortcuts import render
from .models import Job, UploadedFile
from .serializers import JobSerializer
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from utilities.firebase import upload_app_file  # Your utility function for Firebase upload
import mimetypes

# Create your views here.
class JobCreate(generics.CreateAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def perform_create(self, serializer):
        # Automatically associate the current user with the post
        serializer.save(user=self.request.user)

class JobRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    `Authentication` is required
    """
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    lookup_field = 'pk'

class JobFind(APIView):
    """
    `Authentication` is required
    - `GET /jobfind/`: Retrieve all posts
    """
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'title',
                openapi.IN_QUERY,
                description="Returns a Post with specific title but returns all posts if no post matches said title",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request):
        title = request.query_params.get("title", "")

        if title:
            job = Job.objects.filter(title__icontains=title)

        else:
            job = Job.objects.all()
            

        serializer = JobSerializer(job, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class JobWithFileUploadView(APIView):
    """
    `Authentication` is required
    -Set the Authentication to Bearer Token and pass the IdToken
    """
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        # Get the post content from request data
        title = request.data.get('title')
        description = request.data.get('description')
        location = request.data.get('location')
        date_published = request.data.get('date_published')

        if not title:
            return Response({"error": "Post title is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the file from request files
        file = request.FILES.get('file')

        # if not file:
        #     return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)
        if file:
            # Automatically detect content type
            mime_type, encoding = mimetypes.guess_type(file.name)
            content_type = mime_type if mime_type else 'application/octet-stream'

            try:
                # Upload the file to Firebase and get the public URL
                file_url = upload_app_file(file, 'job')

                # Create a job associated with the logged-in user
                job = Job.objects.create(
                    user=request.user,
                    title=title,
                    description=description,
                    location=location,
                    date_published=date_published  # Set post content
                )

                # Save the file URL and associate it with the logged-in user and post
                uploaded_file = UploadedFile.objects.create(
                    user=request.user,  # Associate with the logged-in user
                    file_name=file.name,
                    file_url=file_url,
                    job=job  # Associate the file with the created post
                )

                return Response({
                    "message": "Job and file uploaded successfully.",
                    "job": {
                        "id": job.id,
                        "title": job.title,
                        "username": request.user.display_name,
                        "description": job.description,
                        "location": job.location,
                        "file_url": uploaded_file.file_url,
                        "date_published": job.date_published
                    }
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            try:
                job = Job.objects.create(
                user=request.user,
                title=title,
                description=description,
                location=location,
                date_published=date_published  # Set post content
                )
                return Response({
                    "message": "Job and file uploaded successfully.",
                    "job": {
                        "id": job.id,
                        "title": job.title,
                        "username": request.user.display_name,
                        "description": job.description,
                        "location": job.location,
                        "file_url": None,
                        "date_published": job.date_published
                    }
                    }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    def get(self, request):
        """
        -`GET` Retrieve posts and their uploaded files for the authenticated user.
        """
        try:
            # Get all posts by the authenticated user
            jobs = Job.objects.filter(user=request.user)

            # If no jobs are found, return a response
            if not jobs.exists():
                return Response({"message": "No posts found."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare data for response
            jobs_data = []
            for job in jobs:
                # Get associated uploaded file for each post
                uploaded_file = UploadedFile.objects.filter(job=job).first()
                file_url = uploaded_file.file_url if uploaded_file else None
                
                jobs_data.append({
                    "id": job.id,
                    "title": job.title,
                    "username": request.user.display_name,
                    "description": job.description,
                    "location": job.location,
                    "file_url": file_url,
                    "date_published": job.date_published
                })

            return Response({
                "message": "Jobs retrieved successfully.",
                "posts": jobs_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)