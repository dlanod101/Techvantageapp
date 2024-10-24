from django.shortcuts import render
from .models import Post
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.views import APIView
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone

# Create your views here.
class PostCreate(generics.CreateAPIView):
    """
    `Authentication` is required
    Project CRUD operations.
    - `GET /post/` : Retrieve all post
    - `POST /post/` : Create a new post
    - `PUT /post/{id}/` : Update a post
    - `DELETE /post/{id}/` : Delete a post
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
    - `GET /post/` : Retrieve all posts
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
from utilities.firebase import upload_app_file, delete_file_from_firebase # Your utility function for Firebase upload

class PostWithFileUploadView(APIView):
    """
    `Authentication` is required
    -Set the Authentication to Bearer Token and pass the IdToken
    """
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        # Get the post content from request data
        content = request.data.get('content')
        color_code = request.data.get('color_code')
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
                    color_code=color_code,
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
                        "color_code": post.color_code,
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
                        color_code=color_code,
                        date_published=date_published
                  )  # Set post content

                return Response({
                        "message": "Post and file uploaded successfully.",
                        "post": {
                            "id": post.id,
                            "content": post.content,
                            "color_code": post.color_code,
                            "file_url": None,
                            "date_published": post.date_published
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
                    "color_code": post.color_code,
                    "file_url": file_url,
                    "date_published": post.date_published
                })

            return Response({
                "message": "Posts retrieved successfully.",
                "posts": posts_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class PostWithFileUploadViewSingleFile(APIView):
    """
    -`GET` Retrieve posts and their uploaded files for the authenticated user.
    """
    def get(self, request, post_id):
        try:
            try:
                post = Post.objects.get(id=post_id, user=request.user)
            except Post.DoesNotExist:
                return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare data for response
            posts_data = []
            
        # Get associated uploaded file for each post
            uploaded_file = UploadedFile.objects.filter(post=post).first()
            file_url = uploaded_file.file_url if uploaded_file else None
                    
            posts_data.append({
                "id": post.id,
                "content": post.content,
                "color_code": post.color_code,
                "file_url": file_url,
                "date_published": post.date_published
            }) 

            return Response({
                "message": "Posts retrieved successfully.",
                "posts": posts_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    
    # PUT (Full update)
    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, user=request.user)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('content')
        color_code = request.data.get('color_code')
        date_published = request.data.get('date_published', timezone.now())
        file = request.FILES.get('file')
        

        if not content:
            return Response({"error": "Post content is required."}, status=status.HTTP_400_BAD_REQUEST)

        if file:
            try:
                file_url = upload_app_file(file, 'posts')

                # Update post and uploaded file
                post.content = content
                post.color_code = color_code
                post.date_published = date_published
                post.save()

                uploaded_file, _ = UploadedFile.objects.update_or_create(post=post, defaults={
                    "file_name": file.name,
                    "file_url": file_url,
                    "user": request.user
                })

                return Response({
                    "message": "Post updated successfully.",
                    "post": {
                        "id": post.id,
                        "content": post.content,
                        "color_code": post.color_code,
                        "file_url": uploaded_file.file_url,
                        "date_published": post.date_published
                    }
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            post.content = content
            post.color_code = color_code
            post.date_published = date_published
            post.save()

            return Response({
                "message": "Post updated successfully.",
                "post": {
                    "id": post.id,
                    "content": post.content,
                    "color_code": post.color_code,
                    "file_url": None,
                    "date_published": post.date_published
                }
            }, status=status.HTTP_200_OK)

    # PATCH (Partial update)
    def patch(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, user=request.user)
        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        content = request.data.get('content', post.content)
        color_code = request.data.get("color_code")
        date_published = request.data.get('date_published', post.date_published)
        file = request.FILES.get('file')

        if file:
            try:
                file_url = upload_app_file(file, 'posts')
                post.content = content
                post.color_code = color_code
                post.date_published = date_published
                post.save()

                uploaded_file, _ = UploadedFile.objects.update_or_create(post=post, defaults={
                    "file_name": file.name,
                    "file_url": file_url,
                    "user": request.user
                })

                return Response({
                    "message": "Post partially updated.",
                    "post": {
                        "id": post.id,
                        "content": post.content,
                        "color_code": post.color_code,
                        "file_url": uploaded_file.file_url,
                        "date_published": post.date_published
                    }
                }, status=status.HTTP_200_OK)

            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            post.content = content
            post.color_code = color_code
            post.date_published = date_published
            post.save()

            return Response({
                "message": "Post partially updated.",
                "post": {
                    "id": post.id,
                    "content": post.content,
                    "color_code": post.color_code,
                    "file_url": None,
                    "date_published": post.date_published
                }
            }, status=status.HTTP_200_OK)

    # DELETE (Delete post and associated file)
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, user=request.user)
            uploaded_file = UploadedFile.objects.filter(post=post).first()

            # Delete the file from Firebase storage if it exists
            if uploaded_file:
                try:
                    # Assuming you have a function to delete files from Firebase
                    delete_file_from_firebase("posts/uploads/" + uploaded_file.file_name)
                    uploaded_file.delete()
                except Exception as e:
                    return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            post.delete()

            return Response({"message": "Post and associated file deleted successfully."}, status=status.HTTP_200_OK)

        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)