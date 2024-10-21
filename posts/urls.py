from django.urls import path
from . import views

urlpatterns = [
    path('post/', views.PostCreate.as_view(), name='post-create'),
    path('post/<int:pk>', views.PostRetrieveUpdateDestroy.as_view(), name='post-update'),
    path('post_file_upload/', views.PostWithFileUploadView.as_view(), name='post-file-upload'),
    #path('post_file_retrieve/<int:file_id>', views.RetrieveFileView.as_view(), name='post-file-retrieve'),
]