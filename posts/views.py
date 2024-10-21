from django.shortcuts import render
from .models import Post
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status

# Create your views here.
class PostCreate(generics.CreateAPIView):
    """
    `Authentication` is required
    Project CRUD operations.
    - `GET /posts/` : Retrieve all posts
    - `POST /posts/` : Create a new post
    - `PUT /posts/{id}/` : Update a post
    - `DELETE /posts/{id}/` : Delete a post
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def perform_create(self, serializer):
        # Automatically associate the current user with the post
        serializer.save(user=self.request.user)

class PostRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    """
    `Authentication` is required
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk'



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, UploadedFile  # Models for posts and uploaded files
import mimetypes
import firebase_admin
from firebase_admin import storage
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file  # Your utility function for Firebase upload

class PostWithFileUploadView(APIView):
    """
    `Authentication` is required
    -Set the Authentication to Bearer Token and pass the IdToken
    """
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        # Get the post content from request data
        content = request.data.get('content')
        
        if not content:
            return Response({"error": "Post content is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the file from request files
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Automatically detect content type
        mime_type, encoding = mimetypes.guess_type(file.name)
        content_type = mime_type if mime_type else 'application/octet-stream'

        try:
            # Upload the file to Firebase and get the public URL
            file_url = upload_app_file(file, 'posts')

            # Create a post associated with the logged-in user
            post = Post.objects.create(
                user=request.user,
                content=content  # Set post content
            )

            # Save the file URL and associate it with the logged-in user and post
            uploaded_file = UploadedFile.objects.create(
                user=request.user,  # Associate with the logged-in user
                file_name=file.name,
                file_url=file_url,
                post=post  # Associate the file with the created post
            )

            return Response({
                "message": "Post and file uploaded successfully.",
                "post": {
                    "id": post.id,
                    "content": post.content,
                    "file_url": uploaded_file.file_url
                }
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
