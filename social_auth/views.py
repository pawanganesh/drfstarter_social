import os

from django.utils.http import parse_qsl
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from dotenv import load_dotenv
from requests_oauthlib import OAuth1Session

from .serializers import GoogleSocialAuthSerializer, FacebookSocialAuthSerializer, TwitterAuthSerializer
from utils.token import get_access_token, get_refresh_token

load_dotenv()


class GoogleSocialAuthView(GenericAPIView):
    """
    Google Social Auth View
    This view is used to authenticate users using Google OAuth2.
    {
        "auth_token": "token_received_from_google"
    }
    """
    serializer_class = GoogleSocialAuthSerializer
    permission_classes = [AllowAny, ]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['auth_token']
        access = get_access_token(user)
        refresh = get_refresh_token(user)
        return Response({
            'access': str(access),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class FacebookSocialAuthView(GenericAPIView):
    """
    Facebook Social Auth View
    This view is used to authenticate users using Facebook OAuth2.
    {
        "auth_token": "token_received_from_facebook"
    }
    """

    serializer_class = FacebookSocialAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['auth_token']
        access = get_access_token(user)
        refresh = get_refresh_token(user)
        return Response({
            'access': str(access),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class TwitterSocialAuthView(GenericAPIView):
    serializer_class = TwitterAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class TwitterOAuthTokenRequestView(APIView):
    @staticmethod
    def post(request):
        # create an object of OAuth1Session
        request_token = OAuth1Session(client_key=os.getenv("TWITTER_API_KEY"),
                                      client_secret=os.getenv("TWITTER_API_KEY_SECRET"))

        # twitter endpoint to get request token
        url = "https://api.twitter.com/oauth/request_token"

        # get request_token_key, request_token_secret and other details
        resp = request_token.post(url)

        # convert resp to dict
        response = dict(parse_qsl(resp.text))
        print(resp.content)
        print(response)

        return Response(response, status=status.HTTP_200_OK)
