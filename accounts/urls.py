from django.urls import path
from .views import RegisterAPIView,ProfileAPIView,MeAPIView,EmailTokenObtainPairView,GoogleLoginAPIView
from .views import ( ForgotPasswordAPIView, ResetPasswordAPIView )
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/',RegisterAPIView.as_view()),
    path("login/", EmailTokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view(),name="token_refresh"),
    path("profile/", ProfileAPIView.as_view()),
    path("me/", MeAPIView.as_view()),
    path("google-login/", GoogleLoginAPIView.as_view()),
    path("forgot-password/", ForgotPasswordAPIView.as_view()),
    path("reset-password/<uidb64>/<token>/", ResetPasswordAPIView.as_view()),
]

