"""
Formulaires pour les prescriptions médicales.
"""

from django import forms
from .models import Prescription


class PrescriptionLunettesForm(forms.Form):
    """Formulaire pour ordonnance lunettes."""

    # Oeil droit (OD)
    od_sphere = forms.CharField(
        label='OD Sphère',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: -2.50'})
    )
    od_cylindre = forms.CharField(
        label='OD Cylindre',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: -0.75'})
    )
    od_axe = forms.CharField(
        label='OD Axe',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 170°'})
    )
    od_addition = forms.CharField(
        label='OD Addition',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: +2.00'})
    )

    # Oeil gauche (OG)
    og_sphere = forms.CharField(
        label='OG Sphère',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: -2.00'})
    )
    og_cylindre = forms.CharField(
        label='OG Cylindre',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: -0.50'})
    )
    og_axe = forms.CharField(
        label='OG Axe',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 170°'})
    )
    og_addition = forms.CharField(
        label='OG Addition',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: +2.00'})
    )

    remarques = forms.CharField(
        label='Remarques',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def to_contenu(self):
        """Convertit les données du formulaire en JSON contenu."""
        data = self.cleaned_data
        return {
            'oeil_droit': {
                'sphere': data.get('od_sphere', ''),
                'cylindre': data.get('od_cylindre', ''),
                'axe': data.get('od_axe', ''),
                'addition': data.get('od_addition', ''),
            },
            'oeil_gauche': {
                'sphere': data.get('og_sphere', ''),
                'cylindre': data.get('og_cylindre', ''),
                'axe': data.get('og_axe', ''),
                'addition': data.get('og_addition', ''),
            },
            'remarques': data.get('remarques', ''),
        }


class PrescriptionTraitementForm(forms.Form):
    """Formulaire pour prescription de traitement médical."""

    medicament_1_nom = forms.CharField(
        label='Médicament 1',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du médicament'})
    )
    medicament_1_posologie = forms.CharField(
        label='Posologie',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 1 goutte 3x/jour'})
    )
    medicament_1_duree = forms.CharField(
        label='Durée',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 7 jours'})
    )
    medicament_1_instructions = forms.CharField(
        label='Instructions',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Instructions particulières'})
    )

    medicament_2_nom = forms.CharField(
        label='Médicament 2',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du médicament'})
    )
    medicament_2_posologie = forms.CharField(
        label='Posologie',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 1 goutte 3x/jour'})
    )
    medicament_2_duree = forms.CharField(
        label='Durée',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 7 jours'})
    )
    medicament_2_instructions = forms.CharField(
        label='Instructions',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    medicament_3_nom = forms.CharField(
        label='Médicament 3',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du médicament'})
    )
    medicament_3_posologie = forms.CharField(
        label='Posologie',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    medicament_3_duree = forms.CharField(
        label='Durée',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    medicament_3_instructions = forms.CharField(
        label='Instructions',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    remarques = forms.CharField(
        label='Remarques',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def to_contenu(self):
        data = self.cleaned_data
        medicaments = []
        for i in range(1, 4):
            nom = data.get(f'medicament_{i}_nom', '').strip()
            if nom:
                medicaments.append({
                    'nom': nom,
                    'posologie': data.get(f'medicament_{i}_posologie', ''),
                    'duree': data.get(f'medicament_{i}_duree', ''),
                    'instructions': data.get(f'medicament_{i}_instructions', ''),
                })
        return {
            'medicaments': medicaments,
            'remarques': data.get('remarques', ''),
        }


class PrescriptionExamenForm(forms.Form):
    """Formulaire pour prescription d'examens complémentaires."""

    examen_1_nom = forms.CharField(
        label='Examen 1',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Champ visuel'})
    )
    examen_1_indication = forms.CharField(
        label='Indication',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Indication clinique'})
    )
    examen_1_urgence = forms.ChoiceField(
        label='Urgence',
        required=False,
        choices=[('', 'Normal'), ('urgent', 'Urgent'), ('tres_urgent', 'Très urgent')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    examen_2_nom = forms.CharField(
        label='Examen 2',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    examen_2_indication = forms.CharField(
        label='Indication',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    examen_2_urgence = forms.ChoiceField(
        label='Urgence',
        required=False,
        choices=[('', 'Normal'), ('urgent', 'Urgent'), ('tres_urgent', 'Très urgent')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    examen_3_nom = forms.CharField(
        label='Examen 3',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    examen_3_indication = forms.CharField(
        label='Indication',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    examen_3_urgence = forms.ChoiceField(
        label='Urgence',
        required=False,
        choices=[('', 'Normal'), ('urgent', 'Urgent'), ('tres_urgent', 'Très urgent')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    remarques = forms.CharField(
        label='Remarques',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def to_contenu(self):
        data = self.cleaned_data
        examens = []
        for i in range(1, 4):
            nom = data.get(f'examen_{i}_nom', '').strip()
            if nom:
                examens.append({
                    'nom': nom,
                    'indication': data.get(f'examen_{i}_indication', ''),
                    'urgence': data.get(f'examen_{i}_urgence', ''),
                })
        return {
            'examens': examens,
            'remarques': data.get('remarques', ''),
        }


class PrescriptionLentillesForm(forms.Form):
    """Formulaire pour prescription de lentilles de contact."""

    od_rayon = forms.CharField(
        label='OD Rayon de courbure',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 8.6'})
    )
    od_diametre = forms.CharField(
        label='OD Diamètre',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 14.0'})
    )
    od_puissance = forms.CharField(
        label='OD Puissance',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: -2.50'})
    )
    od_marque = forms.CharField(
        label='OD Marque',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Acuvue'})
    )

    og_rayon = forms.CharField(
        label='OG Rayon de courbure',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 8.6'})
    )
    og_diametre = forms.CharField(
        label='OG Diamètre',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 14.0'})
    )
    og_puissance = forms.CharField(
        label='OG Puissance',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: -2.00'})
    )
    og_marque = forms.CharField(
        label='OG Marque',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    renouvellement = forms.CharField(
        label='Renouvellement',
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: Mensuel'})
    )
    remarques = forms.CharField(
        label='Remarques',
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def to_contenu(self):
        data = self.cleaned_data
        return {
            'oeil_droit': {
                'rayon': data.get('od_rayon', ''),
                'diametre': data.get('od_diametre', ''),
                'puissance': data.get('od_puissance', ''),
                'marque': data.get('od_marque', ''),
            },
            'oeil_gauche': {
                'rayon': data.get('og_rayon', ''),
                'diametre': data.get('og_diametre', ''),
                'puissance': data.get('og_puissance', ''),
                'marque': data.get('og_marque', ''),
            },
            'renouvellement': data.get('renouvellement', ''),
            'remarques': data.get('remarques', ''),
        }
