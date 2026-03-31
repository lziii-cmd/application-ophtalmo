"""
Configuration admin pour l'agenda.
"""

from django.contrib import admin
from .models import RendezVous


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('patient', 'medecin', 'date_heure', 'duree', 'statut', 'motif')
    list_filter = ('statut', 'medecin', 'date_heure')
    search_fields = ('patient__nom', 'patient__prenom', 'medecin__last_name', 'motif')
    ordering = ('-date_heure',)
    readonly_fields = ('date_creation', 'date_modification', 'created_by')
