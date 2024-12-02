from django.urls import path
from . import views

urlpatterns = [
    path('post_file_upload/', views.PostWithFileUploadView.as_view(), name='post-file-upload'),
    path('post_file_upload/<int:post_id>', views.PostWithFileUploadViewSingleFile.as_view(), name='post-details'),
    path('post/<int:post_id>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),
    path('post/<int:post_id>/toggle-like/', views.ToggleLikeView.as_view(), name='toggle-like'),
    path('share/<int:post_id>/', views.SharePostView.as_view(), name='share-post'),
    path('user_post/<int:user_id>', views.UserPostView.as_view(), name='user-post'),
]