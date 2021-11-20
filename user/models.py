from django.db import models
from django.core.validators import MinLengthValidator
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _

from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from .managers import CustomUserManager
from utils.common_models import TimeStampedUUIDModel

AUTH_PROVIDERS = {
    'facebook': 'facebook',
    'google': 'google',
    'twitter': 'twitter',
    'email': 'email',
}


class User(AbstractBaseUser, PermissionsMixin, TimeStampedUUIDModel):
    """
    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()

    full_name = models.CharField(max_length=150, blank=True)
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        error_messages={
            'unique': _("A user with this username already exists."),
        },
    )
    email = models.EmailField(unique=True,
                              error_messages={
                                  'unique': _("A user with this email already exists."),
                              },
                              )
    phone = models.CharField(max_length=15,
                             unique=True,
                             validators=[
                                 MinLengthValidator(10, message='Phone number must be at least 10 digits')
                             ],
                             error_messages={
                                 'unique': _("A user with this phone already exists."),
                             },
                             )
    auth_provider = models.CharField(max_length=20, choices=AUTH_PROVIDERS.items(), default=AUTH_PROVIDERS.get('email'))
    is_staff = models.BooleanField('staff status', default=False)
    is_active = models.BooleanField('active', default=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'phone', ]

    objects = CustomUserManager()

    def tokens(self):
        access_token = AccessToken.for_user(self)
        refresh_token = RefreshToken.for_user(self)
        return {
            'access': access_token,
            'refresh': refresh_token,
        }

    def __str__(self):
        return self.username
