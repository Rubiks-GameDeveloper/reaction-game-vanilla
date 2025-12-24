"""
Admin configuration for accounts app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""
    list_display = ('username', 'email', 'is_guest', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('is_guest', 'is_staff', 'is_active', 'date_joined')
    search_fields = ('username', 'email')
    ordering = ('username',)

