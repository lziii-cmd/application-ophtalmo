"""
Configuration admin pour l'audit - lecture seule.
"""

from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('horodatage', 'utilisateur', 'action', 'entite', 'entite_id', 'ip_address')
    list_filter = ('action', 'entite', 'horodatage')
    search_fields = ('utilisateur__username', 'entite', 'entite_id', 'ip_address')
    ordering = ('-horodatage',)
    readonly_fields = ('horodatage', 'utilisateur', 'action', 'entite', 'entite_id',
                       'valeur_avant', 'valeur_apres', 'ip_address', 'user_agent')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
