from django.urls import path
from .views import JobCreate, JobRetrieveUpdateDestroy, JobFind, JobWithFileUploadView

urlpatterns = [
    path('job/', JobCreate.as_view(), name="job-create"),
    path('job/<int:pk>', JobRetrieveUpdateDestroy.as_view(), name="job-update"),
    path('jobfind/', JobFind.as_view(), name="job-update"),
    path('job_file_upload/', JobWithFileUploadView.as_view(), name='job-file-upload'),
]