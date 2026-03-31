"""
Configuration de l'admin Django pour les comptes utilisateurs.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'get_full_name', 'email', 'role', 'is_active', 'is_locked', 'failed_login_count')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('last_name', 'first_name')

    fieldsets = UserAdmin.fieldsets + (
        ('Informations médicales', {
            'fields': ('role', 'rpps', 'telephone', 'specialite')
        }),
        ('Sécurité', {
            'fields': ('failed_login_count', 'locked_until')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations médicales', {
            'fields': ('role', 'rpps', 'telephone', 'specialite', 'first_name', 'last_name', 'email')
        }),
    )

    def is_locked(self, obj):
        return obj.is_locked
    is_locked.boolean = True
    is_locked.short_description = 'Verrouillé'
