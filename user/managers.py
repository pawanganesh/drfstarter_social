from django.contrib.auth.models import BaseUserManager
from django.utils.translation import ugettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, phone, password, **extra_fields):
        if not username:
            raise ValueError(_('The username must be set'))
        if not email:
            raise ValueError(_('The email must be set'))
        if not phone:
            raise ValueError(_('The phone must be set'))
        user = self.model(username=username, email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,  username, email, phone, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        extra_fields['is_active'] = True
        extra_fields['is_verified'] = True

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(username, email, phone, password, **extra_fields)
