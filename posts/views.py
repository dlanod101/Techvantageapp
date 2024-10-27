from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Post, UploadedFile, Comment  # Models for posts and uploaded files
from .serializers import CommentSerializer
import mimetypes
from rest_framework import generics
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
                        "username": post.user.display_name,
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
                            "username": post.user.display_name,
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
            # Get all posts 
            posts = Post.objects.all()

            # If no posts are found, return a response
            if not posts.exists():
                return Response({"message": "No posts found."}, status=status.HTTP_404_NOT_FOUND)

            # Prepare data for response
            posts_data = []
            for post in posts:
                # Get associated uploaded file for each post
                uploaded_file = UploadedFile.objects.filter(post=post).first()
                file_url = uploaded_file.file_url if uploaded_file else None
                
                # Get comments associated with the post
                comments = post.post_comment.all()  # Use related_name to get comments
                comments_data = [{
                    "id": comment.id,
                    "username": comment.user.display_name,  # Assuming user has display_name
                    "content": comment.content,
                    "date_published": comment.date_published
                } for comment in comments]

                posts_data.append({
                    "id": post.id,
                    "username": post.user.display_name,
                    "content": post.content,
                    "color_code": post.color_code,
                    "file_url": file_url,
                    "date_published": post.date_published,
                    "comments_data": comments_data
                })

            return Response(posts_data, status=status.HTTP_200_OK)

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

            # Get comments associated with the post
            comments = post.post_comment.all()
            comments_data = [{
                "id": comment.id,
                "username": comment.user.display_name,  # Assuming user has display_name
                "content": comment.content,
                "date_published": comment.date_published
            } for comment in comments]

            posts_data.append({
                "id": post.id,
                "username": request.user.display_name,
                "content": post.content,
                "color_code": post.color_code,
                "file_url": file_url,
                "date_published": post.date_published,
                "comments_data":comments_data
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
                        "username": request.user.display_name,
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
                    "username": request.user.display_name,
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
                        "username": request.user.display_name,
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
                    "username": request.user.display_name,
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
        
from .serializers import CommentSerializer
from django.shortcuts import get_object_or_404

class AddCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])  # Get the post instance
        serializer.save(user=self.request.user, post=post)  # Save comment with user and post