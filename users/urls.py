from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView, FileUploadView, RetrieveFileView, refresh_id_token, generate_password_reset_link

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('retrieve/<int:file_id>', RetrieveFileView.as_view(), name='file-retrieve'),
    path('refresh_id_token/', refresh_id_token, name='refresh_id_token'),
    path('send_password_reset_email/', generate_password_reset_link, name='send_password_reset_email'),

    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
