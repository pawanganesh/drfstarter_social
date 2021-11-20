import os
import logging
from requests_oauthlib import OAuth1Session

from django.utils.http import parse_qsl

from rest_framework import serializers

from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class Twitter:
    """
    class to decode user access_token and user access_token_secret
    tokens will combine the user access_token and access_token_secret
    separated by space
    """

    @staticmethod
    def get_access_token(resource_owner_key, resource_owner_secret):
        """
        resource_owner_key: oauth_token
        resource_owner_secret: oauth_verifier
        WHERE:
        oauth_token and oauth_verifier are obtained from the previous step
        """

        oauth = OAuth1Session(
            client_key=os.getenv('TWITTER_API_KEY'),
            client_secret=os.getenv('TWITTER_API_KEY_SECRET'),
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
        )
        headers = {
            "Content-Type": "application/json",
        }
        url = f"https://api.twitter.com/oauth/access_token?oauth_verifier={resource_owner_secret}"

        resp = oauth.post(url, headers=headers)
        response = dict(parse_qsl(resp.text))
        return response

    @staticmethod
    def get_user_data(access_token):
        """
        get_user_data method returns a twitter user profile info

        NOTE:
            https://developer.twitter.com/en/docs/twitter-api/migrate/twitter-api-endpoint-map
            To access this api we need to have Twitter Elevated access.

            {'errors': [{
                'message': 'You currently have Essential access which includes access to
                Twitter API v2 endpoints only. If you need access to this endpoint,
                you’ll need to apply for Elevated access via the Developer Portal.
                You can learn more here:
                https://developer.twitter.com/en/docs/twitter-api/getting-started/about-twitter-api#v2-access-leve',
                'code': 453}]}
        """
        oauth = OAuth1Session(
            client_key=os.getenv('TWITTER_API_KEY'),
            client_secret=os.getenv('TWITTER_API_KEY_SECRET'),
            resource_owner_key=access_token['oauth_token'],
            resource_owner_secret=access_token['oauth_token_secret'],
        )
        headers = {
            "Content-Type": "application/json",
        }
        params = {"include_email": 'true'}
        url = f"https://api.twitter.com/1.1/account/verify_credentials.json"
        resp = oauth.get(url, headers=headers, params=params)
        return resp.json()

    @staticmethod
    def validate_twitter_auth_tokens(oauth_token, oauth_verifier):
        """
        validate_twitter_auth_tokens methods returns a twitter
        user profile info
        """

        consumer_api_key = os.getenv('TWITTER_API_KEY')
        consumer_api_secret_key = os.getenv('TWITTER_API_KEY_SECRET')

        try:
            logger.debug("haha  from validate twitter auth token")
            # print(user_profile_info)
            # return user_profile_info.__dict__

        except Exception as identifier:
            raise serializers.ValidationError({
                "tokens": ["The tokens are invalid or expired"]})
