from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from movie_recommendation_api.users import models


@admin.register(models.BaseUser)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 'username', 'is_active',
        'is_staff', 'is_verified', 'is_superuser'
    )
    list_filter = ('is_active', 'is_staff', 'is_verified', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)

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

    add_fieldsets = (
        ('Authentication', {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_active', 'is_verified', 'is_superuser')
        }),
    )
