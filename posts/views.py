from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file, delete_file_from_firebase
from .models import Post, UploadedFile, Comment, Like, SharedPost
from .serializers import CommentSerializer, LikeSerializer
from django.db import transaction

class PostWithFileUploadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        content = request.data.get('content')
        color_code = request.data.get('color_code')
        date_published = request.data.get('date_published', timezone.now())
        file = request.FILES.get('file')

        if not content:
            return Response({"error": "Post content is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                # Create post
                post = Post.objects.create(
                    user=request.user, content=content, color_code=color_code, date_published=date_published
                )

                # Handle file upload if present
                if file:
                    file_url = upload_app_file(file, 'posts')
                    UploadedFile.objects.create(
                        user=request.user, file_name=file.name, file_url=file_url, post=post
                    )

                response_data = {
                    "id": post.id,
                    "username": post.user.display_name,
                    "content": post.content,
                    "color_code": post.color_code,
                    "file_url": file_url if file else None,
                    "date_published": post.date_published,
                }
                return Response({"message": "Post created successfully.", "post": response_data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        posts = Post.objects.select_related('user').prefetch_related('post_comment', 'for_post').all()
        posts_data = []

        for post in posts:
            file_url = post.for_post.first().file_url if post.for_post.exists() else None
            comments_data = [{
                "id": comment.id,
                "username": comment.user.display_name,
                "content": comment.content,
                "date_published": comment.date_published
            } for comment in post.post_comment.all()]

            posts_data.append({
                "id": post.id,
                "username": post.user.display_name,
                "content": post.content,
                "color_code": post.color_code,
                "file_url": file_url,
                "date_published": post.date_published,
                "comments_data": comments_data,
                "like_count": post.like_count(),
            })

        return Response(posts_data, status=status.HTTP_200_OK)

class PostWithFileUploadViewSingleFile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        post = get_object_or_404(Post.objects.select_related('user').prefetch_related('post_comment', 'for_post'), id=post_id, user=request.user)
        file_url = post.for_post.first().file_url if post.for_post.exists() else None
        comments_data = [{
            "id": comment.id,
            "username": comment.user.display_name,
            "content": comment.content,
            "date_published": comment.date_published
        } for comment in post.post_comment.all()]

        response_data = {
            "id": post.id,
            "username": post.user.display_name,
            "content": post.content,
            "color_code": post.color_code,
            "file_url": file_url,
            "date_published": post.date_published,
            "comments_data": comments_data,
            "like_count": post.like_count(),
        }
        return Response({"message": "Post retrieved successfully.", "post": response_data}, status=status.HTTP_200_OK)

    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, user=request.user)
            uploaded_file = post.for_post.first()

            if uploaded_file:
                delete_file_from_firebase("posts/uploads/" + uploaded_file.file_name)
                uploaded_file.delete()

            post.delete()
            return Response({"message": "Post deleted successfully."}, status=status.HTTP_200_OK)

        except Post.DoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)

# Other views for AddCommentView, ToggleLikeView, etc.


class AddCommentView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def perform_create(self, serializer):
        post = get_object_or_404(Post, id=self.kwargs['post_id'])  # Get the post instance
        serializer.save(user=self.request.user, post=post)  # Save comment with user and post
        
class ToggleLikeView(generics.GenericAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        
        if not created:
            # Like exists, so we remove it (unlike)
            like.delete()
            return Response({"message": "Like removed"}, status=status.HTTP_200_OK)
        
        # Like didn't exist, so it was created
        return Response({"message": "Like added"}, status=status.HTTP_201_CREATED)

class SharePostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        shared_post = SharedPost.objects.create(post=post, user=request.user)
        return Response({
            "message": "Post shared successfully.",
            "shared_post_id": shared_post.id,
            "post_id": post.id,
            "user": request.user.display_name,
            "shared_at": shared_post.shared_at,
        }, status=status.HTTP_201_CREATED)