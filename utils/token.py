from rest_framework_simplejwt.tokens import AccessToken, RefreshToken


def get_access_token(user):
    """
    Generate access token for user
    """
    return AccessToken.for_user(user)


def get_refresh_token(user):
    """
    Generate refresh token for user
    """
    return RefreshToken.for_user(user)


def tokens(user):
    """
    Generate access and refresh tokens for user
    """
    return {
        'access': str(AccessToken.for_user(user)),
        'refresh': str(RefreshToken.for_user(user))
    }
