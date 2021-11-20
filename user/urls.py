import logging
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import (UserRegistrationRequestCreateAPIView, UserLoginRequestAPIView, UserViewSet,
                    UserPasswordChangeRequestAPIView, EmailVerify, RequestPasswordResetEmail, PasswordTokenCheckAPI,
                    SetNewPasswordAPIView)

# Get an instance of a logger
logger = logging.getLogger(__name__)
logger.info('<<<<<HELLO FROM USER URLS>>>>>')

app_name = 'user'
urlpatterns = [
    path('current/', UserViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}),
         name='current-user'),
    path('register/', UserRegistrationRequestCreateAPIView.as_view(), name='token_obtain_pair'),
    path('token/', UserLoginRequestAPIView.as_view(), name="token"),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-change/', UserPasswordChangeRequestAPIView.as_view(), name='password-change'),
    path('email-verify/', EmailVerify.as_view(), name='email-verify'),
    path('request-reset-email/', RequestPasswordResetEmail.as_view(), name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/', PasswordTokenCheckAPI.as_view(), name='password-reset-confirm'),
    path('password-reset-complete/', SetNewPasswordAPIView.as_view(), name='password-reset-complete'),
]
