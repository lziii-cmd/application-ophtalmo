"""
Formulaires pour la gestion de l'agenda.
"""

from django import forms
from django.utils import timezone
from .models import RendezVous
from apps.patients.models import Patient
from apps.accounts.models import CustomUser


class RendezVousForm(forms.ModelForm):
    """Formulaire de création/modification d'un rendez-vous."""

    class Meta:
        model = RendezVous
        fields = ['patient', 'medecin', 'date_heure', 'duree', 'motif', 'statut', 'motif_annulation']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'medecin': forms.Select(attrs={'class': 'form-select'}),
            'date_heure': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'duree': forms.NumberInput(attrs={'class': 'form-control', 'min': 5, 'max': 120, 'step': 5}),
            'motif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motif de consultation'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'motif_annulation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medecin'].queryset = CustomUser.objects.filter(role='medecin', is_active=True)
        self.fields['patient'].queryset = Patient.objects.filter(statut='actif').order_by('nom', 'prenom')
        self.fields['date_heure'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['motif_annulation'].required = False

    def clean(self):
        cleaned_data = super().clean()
        statut = cleaned_data.get('statut')
        motif_annulation = cleaned_data.get('motif_annulation', '').strip()

        if statut == 'annule' and not motif_annulation:
            raise forms.ValidationError(
                "Le motif d'annulation est obligatoire lorsqu'un rendez-vous est annulé."
            )

        # Vérification des conflits (R4)
        date_heure = cleaned_data.get('date_heure')
        medecin = cleaned_data.get('medecin')
        duree = cleaned_data.get('duree', 20)

        if date_heure and medecin and statut in ['programme']:
            # Créer un objet temporaire pour la vérification
            temp_rdv = RendezVous(
                medecin=medecin,
                date_heure=date_heure,
                duree=duree,
            )
            if self.instance.pk:
                temp_rdv.pk = self.instance.pk
            if temp_rdv.check_conflict(exclude_self=bool(self.instance.pk)):
                raise forms.ValidationError(
                    f"Conflit de rendez-vous: le médecin {medecin.get_full_name()} "
                    f"a déjà un rendez-vous qui chevauche ce créneau."
                )

        return cleaned_data
