from django import forms
from .models import Intervention, SuiviPostOp


class InterventionForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            'patient', 'chirurgien', 'consultation_origine',
            'type_intervention', 'type_autre', 'oeil',
            'date_planifiee', 'anesthesie', 'consentement_signe',
            'bilan_pre_op', 'date_rdv_pre_op',
        ]
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'chirurgien': forms.Select(attrs={'class': 'form-select'}),
            'consultation_origine': forms.Select(attrs={'class': 'form-select'}),
            'type_intervention': forms.Select(attrs={'class': 'form-select'}),
            'type_autre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Préciser le type'}),
            'oeil': forms.Select(attrs={'class': 'form-select'}),
            'date_planifiee': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'anesthesie': forms.Select(attrs={'class': 'form-select'}),
            'consentement_signe': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bilan_pre_op': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_rdv_pre_op': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class CompteRenduForm(forms.ModelForm):
    class Meta:
        model = Intervention
        fields = [
            'date_realisation', 'duree_minutes',
            'compte_rendu', 'complications',
            'acuite_post_op_od', 'acuite_post_op_og', 'notes_post_op',
        ]
        widgets = {
            'date_realisation': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'duree_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'compte_rendu': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'complications': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'acuite_post_op_od': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 10/10'}),
            'acuite_post_op_og': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 10/10'}),
            'notes_post_op': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class SuiviPostOpForm(forms.ModelForm):
    class Meta:
        model = SuiviPostOp
        fields = [
            'type_suivi', 'date_prevue', 'date_realisation',
            'realise', 'acuite_od', 'acuite_og',
            'tension_od', 'tension_og', 'notes',
        ]
        widgets = {
            'type_suivi': forms.Select(attrs={'class': 'form-select'}),
            'date_prevue': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_realisation': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'realise': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'acuite_od': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 8/10'}),
            'acuite_og': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: 8/10'}),
            'tension_od': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'tension_og': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
