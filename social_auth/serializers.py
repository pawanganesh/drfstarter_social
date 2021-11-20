import os
import logging
from dotenv import load_dotenv

from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

from utils.social import register_social_user
from utils.google import Google
from utils.facebook import Facebook
from utils.twitter import Twitter

logger = logging.getLogger(__name__)
load_dotenv()


class GoogleSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    @staticmethod
    def validate_auth_token(auth_token):
        user_data = Google.validate(auth_token)
        try:
            user_data['sub']
        except:
            raise serializers.ValidationError(
                'The token is invalid or expired. Please try again.'
            )

        if user_data['aud'] != os.getenv('GOOGLE_CLIENT_ID'):
            raise AuthenticationFailed('oops, who are you?')

        # user_id = user_data['sub']
        email = user_data['email']
        full_name = user_data['name']
        provider = 'google'

        return register_social_user(
            provider=provider, email=email, full_name=full_name)


class FacebookSocialAuthSerializer(serializers.Serializer):
    auth_token = serializers.CharField()

    @staticmethod
    def validate_auth_token(auth_token):
        user_data = Facebook.validate(auth_token)
        try:
            email = user_data['email']
            full_name = user_data['name']
            provider = 'facebook'
            return register_social_user(
                provider=provider,
                email=email,
                full_name=full_name
            )
        except Exception as identifier:
            print("Exception")
            raise serializers.ValidationError(
                'The token  is invalid or expired. Please try again.'
            )


class TwitterAuthSerializer(serializers.Serializer):
    """
    Handles serialization of twitter related data

    TODO:
        - Remember to work on this once I got Twitter Elevated Access
    """
    oauth_token = serializers.CharField()
    oauth_verifier = serializers.CharField()

    def validate(self, attrs):

        oauth_token = attrs.get('oauth_token')
        oauth_verifier = attrs.get('oauth_verifier')

        logger.debug("Hello I am from serializer validate twitter")
        print("Hello I am from serializer validate twitter")

        access_token = Twitter.get_access_token(
            oauth_token, oauth_verifier)
        user_data = Twitter.get_user_data(access_token)
        print(user_data)

        try:
            # user_id = user_info['id_str']
            email = user_data['email']
            full_name = user_data['name']
            provider = 'twitter'
        except:
            raise serializers.ValidationError(
                'The tokens are invalid or expired. Please try again.'
            )

        return register_social_user(
            provider=provider, email=email, full_name=full_name)
