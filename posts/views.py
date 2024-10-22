from django.shortcuts import render
from .models import Post
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

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

class PostFind(APIView):
    """
    `Authentication` is required
    - `GET /posts/` : Retrieve all posts
    """
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'content',
                openapi.IN_QUERY,
                description="Returns a Post with specific content but returns all posts if no post matches said content",
                type=openapi.TYPE_STRING,
            ),
        ],
    )
    def get(self, request):
        content = request.query_params.get("content", "")

        if content:
            post = Post.objects.filter(content__icontains=content)

        else:
            post = Post.objects.all()
            

        serializer = PostSerializer(post, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


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
        date_published = request.data.get('date_published')

        if not content:
            return Response({"error": "Post content is required."}, status=status.HTTP_400_BAD_REQUEST)

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
                file_url = upload_app_file(file, 'posts')

                # Create a post associated with the logged-in user
                post = Post.objects.create(
                    user=request.user,
                    content=content,
                    date_published=date_published  # Set post content
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
                        "file_url": uploaded_file.file_url,
                        "date_published": post.date_published
                    }
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            try:
                post = Post.objects.create(
                        user=request.user,
                        content=content,
                        date_published=date_published
                  )  # Set post content

                return Response({
                        "message": "Post and file uploaded successfully.",
                        "post": {
                            "id": post.id,
                            "content": post.content,
                            "file_url": None,
                            "date_published": post.date_published
                        }
                    }, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    def get(self, request):
        """
        Retrieve posts and their uploaded files for the authenticated user.
        """
        try:
            # Get all posts by the authenticated user
            posts = Post.objects.filter(user=request.user)

            # If no posts are found, return a response
            if not posts.exists():
                return Response({"message": "No posts found."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare data for response
            posts_data = []
            for post in posts:
                # Get associated uploaded file for each post
                uploaded_file = UploadedFile.objects.filter(post=post).first()
                file_url = uploaded_file.file_url if uploaded_file else None
                
                posts_data.append({
                    "id": post.id,
                    "content": post.content,
                    "file_url": file_url,
                    "date_published": post.date_published
                })

            return Response({
                "message": "Posts retrieved successfully.",
                "posts": posts_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)