import logging

from django.urls import reverse
from django.contrib.auth import get_user_model, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed

from utils.email import Email
from utils.token import get_access_token
from utils.password import validate_password

User = get_user_model()
logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user model
    """

    class Meta:
        model = User
        fields = ('id', 'full_name', 'username', 'email',)
        extra_kwargs = {'password': {'read_only': True}}


class UserRegistrationRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration request
    """
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ('full_name', 'username', 'email', 'phone', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    @staticmethod
    def validate_password(value):
        errors = validate_password(value)
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get('email')
        username = attrs.get('username')
        phone = attrs.get('phone')
        if not email:
            raise serializers.ValidationError('Email is required')
        if not username:
            raise serializers.ValidationError('Username is required')
        if not phone:
            raise serializers.ValidationError('Phone is required')
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.is_active = True
        user.save()

        # generate verification token
        token = get_access_token(user)
        current_site = get_current_site(self.context['request']).domain
        relativelink = reverse('user:email-verify')
        absurl = 'http://{0}{1}?token={2}'.format(current_site, relativelink, str(token))

        #  send verification email to user
        # Email.sendgrid_email({
        #     'to': [user.email, ],
        #     'subject': 'Verify your account',
        #     'body': 'Your verification link is {0}'.format(absurl)
        # })

        # send verification email with template to user
        Email.send_html_email("email/user_verification.html", {
            'to': [user.email],
            'subject': 'Verify your account',
            'context': {
                'absurl': absurl,
                'full_name': user.full_name,
            }
        })

        return user


class UserLoginRequestSerializer(serializers.Serializer):
    """
    Serializer for user login request
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(max_length=128, required=True, write_only=True)
    user = serializers.ReadOnlyField

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({'message': 'Invalid credentials'})
        elif user and not user.is_verified:
            # generate verification token
            token = get_access_token(user)
            current_site = get_current_site(self.context['request']).domain
            relativelink = reverse('user:email-verify')
            absurl = 'http://{0}{1}?token={2}'.format(current_site, relativelink, str(token))
            # send verification email with template to user
            Email.send_html_email("email/user_verification.html", {
                'to': [user.email],
                'subject': 'Verify your account',
                'context': {
                    'absurl': absurl,
                    'full_name': user.full_name,
                }
            })
            return AuthenticationFailed({'message': 'Please verify email to continue'})
        elif user.auth_provider != 'email':
            raise AuthenticationFailed({'message': f'Please continue your login using {user.auth_provider}'})
        attrs['user'] = user
        return attrs


class UserPasswordChangeRequestSerializer(serializers.Serializer):
    """
    Serializer for User Password Change
    """

    old_password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    new_password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    confirm_password = serializers.CharField(max_length=128, required=True, write_only=True)

    @staticmethod
    def validate_new_password(value):
        validate_password_errors = validate_password(value)
        if not validate_password_errors:
            return value
        raise serializers.ValidationError(validate_password_errors)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'message': 'New password and confirm password does not match'
            })
        request = self.context.get('request')
        user = authenticate(password=attrs['old_password'], email=request.user.email)
        if not user:
            raise serializers.ValidationError({
                'message': 'Invalid credentials'
            })
        return attrs


class ResetPasswordEmailRequestSerializer(serializers.Serializer):
    """
    Serializer for reset password email request
    """

    email = serializers.EmailField(required=True)
    redirect_url = serializers.CharField(min_length=3, max_length=500, required=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        email = attrs.get('email')
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({'message': 'No account found'})
        attrs['user'] = user
        return attrs


class SetNewPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    token = serializers.CharField(write_only=True)
    uidb64 = serializers.CharField(write_only=True)

    class Meta:
        fields = ('password', 'token', 'uidb64')

    @staticmethod
    def validate_password(value):
        errors = validate_password(value)
        if errors:
            raise serializers.ValidationError(errors)
        return value

    def validate(self, attrs):
        attrs = super().validate(attrs)
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed('The reset link is invalid', status.HTTP_401_UNAUTHORIZED)
            user.set_password(password)
            user.save()
            return attrs
        except Exception as e:
            raise AuthenticationFailed('The reset link is invalid', status.HTTP_401_UNAUTHORIZED)
