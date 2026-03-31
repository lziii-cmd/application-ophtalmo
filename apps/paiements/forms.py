"""
Formulaires pour les paiements.
"""

from django import forms
from .models import Paiement
from apps.patients.models import Patient
from apps.consultations.models import Consultation


class PaiementForm(forms.ModelForm):
    """Formulaire de saisie d'un paiement."""

    class Meta:
        model = Paiement
        fields = [
            'patient', 'consultation', 'montant', 'montant_total_du',
            'date', 'type_paiement', 'mode_paiement',
            'reference_externe', 'notes'
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select', 'id': 'id_patient'}),
            'consultation': forms.Select(attrs={'class': 'form-select', 'id': 'id_consultation'}),
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'montant_total_du': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'type_paiement': forms.Select(attrs={'class': 'form-select'}),
            'mode_paiement': forms.Select(attrs={'class': 'form-select'}),
            'reference_externe': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'N° chèque, réf. virement...'
            }),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        patient_id = kwargs.pop('patient_id', None)
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%Y-%m-%d']
        self.fields['consultation'].required = False
        self.fields['montant_total_du'].required = False
        self.fields['patient'].queryset = Patient.objects.filter(statut='actif').order_by('nom', 'prenom')

        if patient_id:
            self.fields['consultation'].queryset = Consultation.objects.filter(
                patient_id=patient_id
            ).order_by('-date_heure')
        else:
            self.fields['consultation'].queryset = Consultation.objects.none()

    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant is not None and montant <= 0:
            raise forms.ValidationError("Le montant doit être supérieur à 0.")
        return montant
