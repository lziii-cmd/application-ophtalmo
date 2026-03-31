"""
Configuration admin pour les patients.
"""

from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'date_naissance', 'age', 'telephone', 'statut', 'date_creation')
    list_filter = ('statut', 'sexe')
    search_fields = ('nom', 'prenom', 'telephone', 'email')
    ordering = ('nom', 'prenom')
    readonly_fields = ('date_creation', 'date_modification')

    fieldsets = (
        ('Identité', {
            'fields': ('nom', 'prenom', 'date_naissance', 'sexe')
        }),
        ('Coordonnées', {
            'fields': ('telephone', 'adresse', 'email')
        }),
        ('Informations médicales', {
            'fields': ('antecedents', 'allergies', 'traitements_en_cours')
        }),
        ('Statut', {
            'fields': ('statut', 'date_creation', 'date_modification')
        }),
    )

    def has_delete_permission(self, request, obj=None):
        """Désactiver la suppression physique - R2."""
        return False
