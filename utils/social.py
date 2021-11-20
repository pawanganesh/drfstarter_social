import os

from django.contrib.auth import authenticate, get_user_model

from rest_framework.exceptions import AuthenticationFailed
from dotenv import load_dotenv

User = get_user_model()
load_dotenv()


def generate_username(name):
    username = "".join(name.split(' ')).lower()
    counter = 1
    while User.objects.filter(username=username):
        username = username + str(counter)
        counter += 1
    return username


def register_social_user(provider, email, full_name):
    filtered_user_by_email = User.objects.filter(email=email)

    if filtered_user_by_email.exists():

        if provider == filtered_user_by_email[0].auth_provider:

            user = authenticate(
                email=email, password=os.getenv('SOCIAL_SECRET'))
            return user

        else:
            raise AuthenticationFailed(
                detail='Please continue your login using ' + filtered_user_by_email[0].auth_provider)

    else:
        user = {
            'full_name': full_name,
            'username': generate_username(full_name),
            'email': email,
            'phone': '1800009990',
            'password': os.getenv('SOCIAL_SECRET')}
        user = User.objects.create_user(**user)
        user.is_verified = True
        user.auth_provider = provider
        user.save()

        user = authenticate(
            email=email, password=os.environ.get('SOCIAL_SECRET'))
        return user
