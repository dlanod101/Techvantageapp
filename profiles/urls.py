from django.urls import path
from . import views

urlpatterns = [
    # UserProfile
    path('profile/', views.UserProfileDetailView.as_view(), name='user-profile-detail'),

    # Experience
    path('profile/experiences/', views.ExperienceListCreateView.as_view(), name='experience-list-create'),

    # Education
    path('profile/educations/', views.EducationListCreateView.as_view(), name='education-list-create'),

    # Location
    path('profile/locations/', views.LocationListCreateView.as_view(), name='location-list-create'),

    # Profile Picture
    path('profile/pictures/', views.ProfilePictureListCreateView.as_view(), name='profile-picture-list-create'),
]
