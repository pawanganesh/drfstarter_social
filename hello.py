import os
from requests_oauthlib import OAuth1Session
from dotenv import load_dotenv

from django.utils.http import parse_qsl

load_dotenv()

# NOTE: This file is for testing purposes only. And not part of this project.
oauth_token = "" # oauth_token received from twitter after authorization
oauth_verifier = "" # oauth_verifier received from twitter after authorization


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
    url = f"https://api.twitter.com/oauth/access_token?oauth_verifier={oauth_verifier}"

    resp = oauth.post(url, headers=headers)
    response = dict(parse_qsl(resp.text))
    return response


def get_user_data(access_token):
    print(access_token['oauth_token'])
    print(access_token['oauth_token_secret'])
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


access_token1 = get_access_token(oauth_token, oauth_verifier)
print("access_token")
print(access_token1)

user_data = get_user_data(access_token1)
print(user_data)
