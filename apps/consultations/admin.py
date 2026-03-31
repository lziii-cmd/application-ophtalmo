"""
Configuration admin pour les consultations.
"""

from django.contrib import admin
from .models import Consultation


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_heure', 'statut', 'diagnostic_principal')
    list_filter = ('statut', 'medecin', 'date_heure')
    search_fields = ('patient__nom', 'patient__prenom', 'diagnostic_principal', 'code_cim10_principal')
    ordering = ('-date_heure',)
    readonly_fields = ('date_creation', 'date_modification', 'date_validation')

    def has_delete_permission(self, request, obj=None):
        """Désactiver la suppression physique."""
        return False
