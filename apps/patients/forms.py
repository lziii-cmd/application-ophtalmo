"""
Formulaires pour la gestion des patients.
"""

from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    """Formulaire de création/modification d'un patient."""

    class Meta:
        model = Patient
        fields = [
            'nom', 'prenom', 'date_naissance', 'sexe',
            'telephone', 'adresse', 'email',
            'antecedents', 'allergies', 'traitements_en_cours'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'date_naissance': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'},
                format='%Y-%m-%d'
            ),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '06 00 00 00 00'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemple.com'}),
            'antecedents': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Antécédents médicaux personnels et familiaux...'
            }),
            'allergies': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Allergies connues (médicaments, aliments, etc.)...'
            }),
            'traitements_en_cours': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Traitements médicamenteux en cours...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date_naissance'].input_formats = ['%Y-%m-%d']

    def clean_nom(self):
        nom = self.cleaned_data.get('nom', '')
        return nom.strip().upper()

    def clean_prenom(self):
        prenom = self.cleaned_data.get('prenom', '')
        return prenom.strip().title()


class PatientSearchForm(forms.Form):
    """Formulaire de recherche multicritères de patients."""

    q = forms.CharField(
        label='Recherche',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nom, prénom, téléphone ou numéro patient...',
            'autofocus': True,
        })
    )
    statut = forms.ChoiceField(
        label='Statut',
        required=False,
        choices=[
            ('', 'Tous'),
            ('actif', 'Actifs seulement'),
            ('archive', 'Archivés seulement'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
