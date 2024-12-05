from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from utilities.firebase import upload_app_file, delete_file_from_firebase
from .models import Post, UploadedFile, Comment, Like
from .serializers import CommentSerializer, LikeSerializer
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from profiles.models import UserProfile, ProfilePicture
from django.db.models import Prefetch

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
        # Optimize database queries
        current_user = request.user
        friend_ids = Friend.objects.filter(user=current_user).values_list('friend_id', flat=True)
        posts = Post.objects.filter(Q(user=current_user) | Q(user__id__in=friend_ids)).select_related('user').prefetch_related(
            Prefetch(
                'post_comment',
                queryset=Comment.objects.select_related('user').only(
                    'id', 'user__display_name'
                ),
                to_attr='prefetched_comments'
            ),
            Prefetch(
                'for_post',
                queryset=UploadedFile.objects.only('file_url'),
                to_attr='prefetched_files'
            ),
            Prefetch(
                'user__profile_user',
                queryset=UserProfile.objects.prefetch_related(
                    Prefetch(
                        'profile_pictures',
                        queryset=ProfilePicture.objects.only('file_url'),
                        to_attr='prefetched_profile_pictures'
                    )
                ).only('id'),
                to_attr='prefetched_profile'
            )
        ).only(
            'id', 'user__uid', 'user__display_name', 'content', 'color_code', 'date_published'
        )

        # Build posts data using preloaded data
        posts_data = [
            {
                "id": post.id,
                "userid": (profile := post.user.prefetched_profile[0]).id if post.user.prefetched_profile else None,
                "profile_picture": profile.prefetched_profile_pictures[0].file_url if profile and profile.prefetched_profile_pictures else None,
                "username": post.user.display_name,
                "content": post.content,
                "color_code": post.color_code,
                "file_url": post.prefetched_files[0].file_url if post.prefetched_files else None,
                "date_published": post.date_published,
                "comments_data": [
                    {
                        "id": comment.id,
                        
                    }
                    for comment in post.prefetched_comments
                    ],
                "like_count": post.like_count(),
            }
            for post in posts
        ]

        return Response(posts_data, status=status.HTTP_200_OK)


class PostWithFileUploadViewSingleFile(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request, post_id):
        try:
            # Retrieve the post or raise an exception if not found
            post = Post.objects.get(id=post_id)
            profile_picture = ProfilePicture.objects.get(user=post.user)
            profile = UserProfile.objects.get(user=post.user)
            
            

            # Fetch related data if available
            file_url = post.for_post.first().file_url if post.for_post.exists() else None  # Assuming for_post is the related name for UploadedFile
            comments_data = []
            for comment in post.post_comment.all():
                comment_profile_picture = ProfilePicture.objects.get(user=comment.user)
                comment_profile = UserProfile.objects.get(user=comment.user)
                comments_data.append({
                    "id": comment.id,
                    "profile_id": comment_profile.id,
                    "username": comment.user.display_name,  # Assuming comment has a user field with display_name
                    "profile_picture": comment_profile_picture.file_url,
                    "content": comment.content,
                    "date_published": comment.date_published # Convert to ISO format
                })  # Assuming post_comment is the related name for Comment

            response_data = {
                "id": post.id,
                "profile_id": profile.id,
                "username": post.user.display_name,  # Assuming post has a user field with display_name
                "profile_picture": profile_picture.file_url,
                "content": post.content,
                "color_code": post.color_code,
                "file_url": file_url,
                "date_published": post.date_published,  # Convert to ISO format
                "comments_data": comments_data,
                "like_count": post.like_count(),  # Assuming you have a method to get the like count
            }

            return Response({"message": "Post retrieved successfully.", "post": response_data}, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "Post not found."}, status=status.HTTP_404_NOT_FOUND)


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

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)

        # Generate the URL for the uploaded post
        post_url = f"http://localhost:5173/viewpost/{post_id}"

        return Response({
            "message": "Post URL retrieved successfully.",
            "post_url": post_url,
            "post_id": post.id,
            "user": request.user.display_name,
        }, status=status.HTTP_200_OK)

class UserPostView(APIView):
    permission_classes = [IsAuthenticated]

    
    def get(self, request, user_id):
        
        profile = UserProfile.objects.get(id=user_id)
        # Optimize database queries
        posts = Post.objects.filter(user=profile.user).prefetch_related(
            Prefetch(
                'post_comment',
                queryset=Comment.objects.select_related('user').only(
                    'id', 'content', 'date_published', 'user__display_name'
                ),
                to_attr='prefetched_comments'
            ),
            Prefetch(
                'for_post',
                queryset=UploadedFile.objects.only('file_url'),
                to_attr='prefetched_files'
            ),
            Prefetch(
                'user__profile_user',
                queryset=UserProfile.objects.prefetch_related(
                    Prefetch(
                        'profile_pictures',
                        queryset=ProfilePicture.objects.only('file_url'),
                        to_attr='prefetched_profile_pictures'
                    )
                ).only('id'),
                to_attr='prefetched_profile'
            )
        ).only(
            'id', 'user__uid', 'user__display_name', 'content', 'color_code', 'date_published'
        )

        # Build posts data using preloaded data
        posts_data = [
            {
                "id": post.id,
                "userid": (profile := post.user.prefetched_profile[0]).id if post.user.prefetched_profile else None,
                "profile_picture": profile.prefetched_profile_pictures[0].file_url if profile and profile.prefetched_profile_pictures else None,
                "username": post.user.display_name,
                "content": post.content,
                "color_code": post.color_code,
                "file_url": post.prefetched_files[0].file_url if post.prefetched_files else None,
                "date_published": post.date_published,
                "comments_data": [
                    {
                        "id": comment.id,
                        "userid": profile.id if profile else None,
                        "profile_picture": profile.prefetched_profile_pictures[0].file_url if profile and profile.prefetched_profile_pictures else None,
                        "username": comment.user.display_name,
                        "content": comment.content,
                        "date_published": comment.date_published,
                    }
                    for comment in post.prefetched_comments
                ],
                "like_count": post.like_count(),
            }
            for post in posts
        ]

        return Response(posts_data, status=status.HTTP_200_OK)
