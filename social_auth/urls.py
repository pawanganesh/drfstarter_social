from django.urls import path

from .views import GoogleSocialAuthView, FacebookSocialAuthView, TwitterSocialAuthView, TwitterOAuthTokenRequestView

app_name = 'social_auth'
urlpatterns = [
    path('google/', GoogleSocialAuthView.as_view(), name='google'),
    path('facebook/', FacebookSocialAuthView.as_view(), name='facebook'),
    path('twitter/', TwitterSocialAuthView.as_view(), name='twitter'),

    path('twitter/oauth/request_token/', TwitterOAuthTokenRequestView.as_view(), name='twitter_oauth_token'),
]
