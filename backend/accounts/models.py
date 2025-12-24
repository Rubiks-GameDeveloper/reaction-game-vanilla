"""
Custom User model and related models for accounts app.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    email = models.EmailField(
        unique=True,
        verbose_name='Email'
    )
    is_guest = models.BooleanField(
        default=False,
        verbose_name='Гость'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username

    @property
    def is_authorized_user(self):
        """Check if user is authorized (not guest and not staff/admin)."""
        return not self.is_guest and not self.is_staff

