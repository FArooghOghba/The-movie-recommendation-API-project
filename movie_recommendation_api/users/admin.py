from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from movie_recommendation_api.users import models


@admin.register(models.BaseUser)
class UserAdmin(BaseUserAdmin):
    """
    Custom UserAdmin class for the BaseUser model.

    This class customizes the Django admin interface for the BaseUser model.
    It defines the fields to display in the list view, the filters to apply,
    the fields to search, and the ordering of the users.

    It also customizes the fieldsets to display when adding or editing a user,
    and defines custom fieldsets for adding a new user.
    """

    list_display = (
        'email', 'username', 'is_active',
        'is_staff', 'is_verified', 'is_superuser'
    )
    list_filter = ('is_active', 'is_staff', 'is_verified', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)

    # Fieldsets to display when adding or editing a user
    fieldsets = (
        ('Authentication', {
            'fields': ('email', 'username', 'password')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_verified', 'is_superuser')
        }),
        ('Group Permissions', {
            'fields': ('groups', 'user_permissions')
        }),
        ('Important Date', {
            'fields': ('last_login',)
        }),
    )

    # Custom fieldsets for adding a new user
    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_verified', 'is_superuser')
        }),
    )


@admin.register(models.Profile)
class UserProfileAdmin(admin.ModelAdmin):

    """
    Admin class for managing user profiles.

    This admin class allows administrators to view and manage user profiles,
    including their associated data such as first name, last name, profile picture,
    biography, favorite genres, watchlist, ratings, and reviews.

    Attributes:
        list_display (tuple): The fields to display in the list view of user
        profiles.
        By default, it displays the user's email.
        ordering (tuple): The fields by which the user profiles are ordered in
        the list view.
        By default, it orders profiles by their creation date.
    """

    list_display = (
        'user',
    )
    ordering = ('created_at',)
