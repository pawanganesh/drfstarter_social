import os

import jwt
from dotenv import load_dotenv

from django.shortcuts import render, reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils.encoding import smart_bytes, smart_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect

from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .serializers import UserRegistrationRequestSerializer, UserLoginRequestSerializer, UserSerializer, \
    UserPasswordChangeRequestSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer
from utils.email import Email

User = get_user_model()
load_dotenv()


class CustomRedirect(HttpResponsePermanentRedirect):
    allowed_schemes = [os.getenv('APP_SCHEME'), 'http', 'https']


class UserViewSet(ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user


class UserRegistrationRequestCreateAPIView(CreateAPIView):
    """User create"""
    queryset = User.objects.all()
    serializer_class = UserRegistrationRequestSerializer
    permission_classes = [AllowAny, ]


class UserLoginRequestAPIView(APIView):
    """User login"""
    permission_classes = [AllowAny, ]

    @staticmethod
    def post(request: Request):
        serializer = UserLoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        return Response({
            "access": str(access_token),
            "refresh": str(refresh_token),
        })


class UserPasswordChangeRequestAPIView(APIView):
    """User password change"""
    serializer_class = UserPasswordChangeRequestSerializer
    permission_classes = [IsAuthenticated, ]

    @staticmethod
    def post(request: Request):
        serializer = UserPasswordChangeRequestSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


class EmailVerify(APIView):
    """Email verification"""
    permission_classes = [AllowAny, ]

    @staticmethod
    def get(request):
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.filter(pk=payload['user_id']).first()
            if user is None:
                return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
            elif user.is_verified:
                return Response({'message': 'Account already verified'}, status=status.HTTP_200_OK)
            else:
                user.is_verified = True
                user.save()
                return Response({'message': 'Account successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'message': 'Activation token expired. Please request new one.'},
                            status=status.HTTP_400_BAD_REQUEST)
        except jwt.InvalidTokenError or jwt.DecodeError:
            return Response({'message': 'Activation token is invalid. Please request new one.'},
                            status=status.HTTP_400_BAD_REQUEST)


class RequestPasswordResetEmail(GenericAPIView):
    """Request password reset email"""
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        uidb64 = urlsafe_base64_encode(smart_bytes(user.pk))
        token = PasswordResetTokenGenerator().make_token(user)
        current_site = get_current_site(request).domain
        relativelink = reverse('user:password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})
        redirect_url = serializer.validated_data['redirect_url']
        absurl = f'http://{current_site}{relativelink}?redirect_url={redirect_url}'

        # send email
        # Email.send_email({
        #     'to': [user.email],
        #     'subject': 'Reset password',
        #     'body': 'Your password reset link is {0}'.format(absurl)
        # })

        # send email with template
        Email.send_html_email("email/password-reset.html", {
            'to': [user.email],
            'subject': 'Reset password',
            'context': {
                'absurl': absurl,
            }
        })
        return Response({"message": "Password reset link sent to your email"}, status=status.HTTP_200_OK)


class PasswordTokenCheckAPI(APIView):
    @staticmethod
    def get(request, uidb64, token):
        redirect_url = request.GET.get('redirect_url', '')

        try:
            uid = smart_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)

            if not PasswordResetTokenGenerator().check_token(user, token):
                if redirect_url and len(redirect_url) > 3:
                    return CustomRedirect(redirect_url + '?token_valid=false')
                else:
                    return CustomRedirect(os.getenv("FRONTEND_URL", '') + '?token_valid=false')
                # return Response({"message": "Token is not valid, please request a new one."},
                #                 status=status.HTTP_400_BAD_REQUEST)
            if redirect_url and len(redirect_url) > 3:
                return CustomRedirect(
                    redirect_url + '?token_valid=true?message=tokenvalid?uidb64=' + uidb64 + '?token=' + token)
            else:
                return CustomRedirect(os.getenv("FRONTEND_URL", '') + '?token_valid=true')
            # return Response({'valid': True, 'message': 'Token is valid', 'uidb64': uidb64, 'token': token},
            #                 status=status.HTTP_200_OK)

        except DjangoUnicodeDecodeError:
            if len(redirect_url) > 3:
                return CustomRedirect(redirect_url + '?token_valid=False')
            return Response({"message": "Token is not valid, please request a new one."},
                            status=status.HTTP_400_BAD_REQUEST)


class SetNewPasswordAPIView(APIView):
    """Set new password"""
    serializer_class = SetNewPasswordSerializer
    permission_classes = [AllowAny, ]

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)


def error_404(request, exception):
    return render(request, 'error_404.html')
