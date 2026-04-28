from django.urls import path
from .views import RegisterView, PasswordLoginView, FaceLoginView, LogoutView
from .views_profile import UserProfileView

app_name = 'face'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/password/', PasswordLoginView.as_view(), name='password_login'),
    path('auth/login/face/', FaceLoginView.as_view(), name='face_login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('user/profile/', UserProfileView.as_view(), name='profile'),
]
