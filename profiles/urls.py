from django.urls import path
from . import views

urlpatterns = [
    # UserProfile
    path('profile/', views.UserProfileDetailView.as_view(), name='user-profile-detail'),

    path('profile/<int:pk>/', views.SpecificUserProfileDetailView.as_view(), name='specific-user-profile-detail'),

    # UserProfile
    path('profile_all/', views.ProfileFind.as_view(), name='user-profile-detail-all'),

    # Experience
    path('profile/experiences/', views.ExperienceListCreateView.as_view(), name='experience-list-create'),


    path('profile/experiences/<int:pk>/', views.ExperienceUpdateDelete.as_view(), name='experience-update-delete'),

    # Education
    path('profile/educations/', views.EducationListCreateView.as_view(), name='education-list-create'),


    path('profile/educations/<int:pk>/', views.EducationUpdateDelete.as_view(), name='education-update-delete'),


    # Location
    path('profile/locations/', views.LocationListCreateView.as_view(), name='location-list-create'),


    path('profile/locations/<int:pk>/', views.LocationUpdateDelete.as_view(), name='education-update-delete'),


    # Profile Picture
    path('profile/profilepicture/', views.ProfilePictureUpdateView.as_view(), name='profile-picture-list-create'),

     # Cover Picture
    path('profile/coverpicture/', views.CoverPictureUpdateView.as_view(), name='cover-picture-list-create'),
    
    path('send_friend_request/<str:receiver_uid>/', views.send_friend_request, name='send_friend_request'),

    path('list_friend_requests/', views.list_friend_requests, name='list_friend_requests'),

    path('accept_friend_request/<str:sender_uid>/', views.accept_friend_request, name='accept_friend_request'),

    path('list_friends/', views.list_friends, name='list_friends'),
]
