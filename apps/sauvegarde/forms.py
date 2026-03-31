"""
Formulaires pour la sauvegarde.
"""

from django import forms


class SauvegardeManuelleForm(forms.Form):
    """Formulaire pour déclencher une sauvegarde manuelle."""

    TYPE_CHOICES = [
        ('auto', 'Automatique (1ère du jour = complète, sinon incrémentale)'),
        ('complete', 'Complète'),
        ('incrementale', 'Incrémentale'),
    ]

    type_sauvegarde = forms.ChoiceField(
        label='Type de sauvegarde',
        choices=TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='auto'
    )
