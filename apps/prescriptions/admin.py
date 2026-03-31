"""
Configuration admin pour les prescriptions.
"""

from django.contrib import admin
from .models import Prescription


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('consultation', 'type_prescription', 'medecin', 'date_creation', 'imprimee')
    list_filter = ('type_prescription', 'imprimee', 'medecin')
    search_fields = ('consultation__patient__nom', 'consultation__patient__prenom')
    ordering = ('-date_creation',)
    readonly_fields = ('date_creation',)
