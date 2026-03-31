"""
Serializers DRF pour les consultations.
"""

from rest_framework import serializers
from .models import Consultation


class ConsultationSerializer(serializers.ModelSerializer):
    patient_nom = serializers.CharField(source='patient.nom_complet', read_only=True)
    medecin_nom = serializers.CharField(source='medecin.get_full_name', read_only=True)
    statut_display = serializers.CharField(source='get_statut_display', read_only=True)

    class Meta:
        model = Consultation
        fields = [
            'id', 'patient', 'patient_nom', 'medecin', 'medecin_nom',
            'date_heure', 'statut', 'statut_display',
            'acuite_od_loin', 'acuite_og_loin', 'acuite_od_pres', 'acuite_og_pres',
            'tension_od', 'tension_og',
            'diagnostic_principal', 'code_cim10_principal',
            'date_creation', 'date_modification',
        ]
        read_only_fields = ['id', 'date_creation', 'date_modification']
