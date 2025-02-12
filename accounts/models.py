from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.db import models

from core import settings


class CustomUser(AbstractUser):
    default_currency = models.CharField(max_length=3, choices=settings.CURRENCIES, default="EUR")

    def __str__(self):
        return self.username
