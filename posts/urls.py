from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.PostCreate.as_view(), name='post-create'),
    path('post/<int:pk>', views.PostRetrieveUpdateDestroy.as_view(), name='post-update'),
    path('postfind/', views.PostFind.as_view(), name='post-find'),
    path('post_file_upload/', views.PostWithFileUploadView.as_view(), name='post-file-upload'),
    path('post_file_upload/<int:post_id>', views.PostWithFileUploadViewSingleFile.as_view(), name='post-details'),
    #path('post_file_retrieve/<int:file_id>', views.RetrieveFileView.as_view(), name='post-file-retrieve'),
]