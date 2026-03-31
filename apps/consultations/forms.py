"""
Formulaires pour les consultations médicales.
"""

from django import forms
from .models import Consultation
from apps.patients.models import Patient
from apps.agenda.models import RendezVous
from apps.accounts.models import CustomUser


class ConsultationForm(forms.ModelForm):
    """Formulaire de création/modification d'une consultation."""

    class Meta:
        model = Consultation
        fields = [
            'patient', 'rendez_vous', 'date_heure',
            'acuite_od_loin', 'acuite_og_loin', 'acuite_od_pres', 'acuite_og_pres',
            'tension_od', 'tension_og',
            'diagnostic_principal', 'code_cim10_principal',
            'actes_realises', 'observations',
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'rendez_vous': forms.Select(attrs={'class': 'form-select'}),
            'date_heure': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'acuite_od_loin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: 10/10'
            }),
            'acuite_og_loin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: 10/10'
            }),
            'acuite_od_pres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: P2'
            }),
            'acuite_og_pres': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: P2'
            }),
            'tension_od': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'mmHg',
                'step': '0.5',
                'min': '0',
                'max': '60'
            }),
            'tension_og': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'mmHg',
                'step': '0.5',
                'min': '0',
                'max': '60'
            }),
            'diagnostic_principal': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Diagnostic principal de la consultation...'
            }),
            'code_cim10_principal': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ex: H52.1'
            }),
            'actes_realises': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Actes médicaux réalisés durant la consultation...'
            }),
            'observations': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Observations cliniques, notes complémentaires...'
            }),
        }

    def __init__(self, *args, **kwargs):
        medecin = kwargs.pop('medecin', None)
        super().__init__(*args, **kwargs)
        self.fields['date_heure'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['patient'].queryset = Patient.objects.filter(statut='actif').order_by('nom', 'prenom')
        self.fields['rendez_vous'].required = False
        self.fields['rendez_vous'].queryset = RendezVous.objects.filter(
            statut='programme'
        ).order_by('-date_heure')

        if medecin:
            self.fields['rendez_vous'].queryset = RendezVous.objects.filter(
                medecin=medecin,
                statut='programme'
            ).order_by('-date_heure')


class ConsultationCancelForm(forms.Form):
    """Formulaire d'annulation d'une consultation validée."""

    motif_annulation = forms.CharField(
        label='Motif d\'annulation',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Saisir le motif d\'annulation...',
        }),
        min_length=10,
        error_messages={
            'min_length': 'Le motif d\'annulation doit comporter au moins 10 caractères.',
            'required': 'Le motif d\'annulation est obligatoire.',
        }
    )
