from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):
    date_joined = models.DateTimeField(default=timezone.now, editable=False)
    email = models.EmailField(unique=True, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    name = models.CharField(max_length=255)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []