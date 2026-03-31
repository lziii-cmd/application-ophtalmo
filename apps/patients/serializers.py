"""
Serializers DRF pour les patients.
"""

from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    nom_complet = serializers.CharField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    sexe_display = serializers.CharField(source='get_sexe_display', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = Patient
        fields = [
            'id', 'nom', 'prenom', 'nom_complet', 'date_naissance', 'age',
            'sexe', 'sexe_display', 'telephone', 'email', 'adresse',
            'statut', 'statut_display', 'has_allergies',
            'date_creation', 'date_modification',
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']
