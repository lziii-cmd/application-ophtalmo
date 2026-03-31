"""
Configuration admin pour les paiements.
"""

from django.contrib import admin
from .models import Paiement


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('patient', 'montant', 'type_paiement', 'mode_paiement', 'date', 'valide', 'created_by')
    list_filter = ('type_paiement', 'mode_paiement', 'valide', 'date')
    search_fields = ('patient__nom', 'patient__prenom', 'reference_externe')
    ordering = ('-date', '-date_creation')
    readonly_fields = ('date_creation', 'date_modification', 'created_by')
