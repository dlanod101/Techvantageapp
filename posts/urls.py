from django.urls import path
from . import views

urlpatterns = [
    path('post_file_upload/', views.PostWithFileUploadView.as_view(), name='post-file-upload'),
    path('post_file_upload/<int:post_id>', views.PostWithFileUploadViewSingleFile.as_view(), name='post-details'),
    path('post/<int:post_id>/add_comment/', views.AddCommentView.as_view(), name='add_comment'),
]