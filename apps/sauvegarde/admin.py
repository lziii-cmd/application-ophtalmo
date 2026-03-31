"""
Configuration admin pour les sauvegardes.
"""

from django.contrib import admin
from .models import Sauvegarde


@admin.register(Sauvegarde)
class SauvegardeAdmin(admin.ModelAdmin):
    list_display = ('date_heure', 'type_sauvegarde', 'statut', 'taille_lisible', 'nombre_enregistrements', 'created_by')
    list_filter = ('type_sauvegarde', 'statut')
    ordering = ('-date_heure',)
    readonly_fields = ('date_heure', 'type_sauvegarde', 'fichier_path', 'taille_octets',
                       'statut', 'nombre_enregistrements', 'created_by', 'message_erreur')

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
