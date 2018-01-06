from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager as BaseUserManager
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email: str, password: str = None, is_staff: bool = False, is_active: bool = True,
                    username: str = '', **extra_fields: dict) -> 'User':
        email = UserManager.normalize_email(email)
        user = self.model(email=email, is_active=is_active, is_staff=is_staff, **extra_fields)

        if password:
            user.set_password(password)

        user.save()
        return user

    def create_superuser(self, email: str, password: str = None, **extra_fields: dict) -> 'User':
        return self.create_user(email, password, is_staff=True, is_superuser=True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    name = models.CharField(max_length=255)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
