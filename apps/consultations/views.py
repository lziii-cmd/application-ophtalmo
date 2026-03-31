"""
Vues pour les consultations médicales.
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import Consultation
from .forms import ConsultationForm, ConsultationCancelForm
from apps.accounts.decorators import role_required, medecin_required
from apps.patients.models import Patient
from apps.audit.utils import log_action


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def consultation_list_view(request):
    """Liste des consultations."""
    consultations = Consultation.objects.select_related('patient', 'medecin').all()

    # Filtres
    statut = request.GET.get('statut', '')
    patient_id = request.GET.get('patient', '')
    medecin_id = request.GET.get('medecin', '')

    if statut:
        consultations = consultations.filter(statut=statut)
    if patient_id:
        consultations = consultations.filter(patient_id=patient_id)
    if medecin_id:
        consultations = consultations.filter(medecin_id=medecin_id)

    # Pour la secrétaire: vue partielle (pas les diagnostics détaillés)
    is_partial_view = request.user.is_secretaire

    return render(request, 'consultations/list.html', {
        'consultations': consultations[:50],
        'is_partial_view': is_partial_view,
        'statut_filter': statut,
    })


@login_required
@role_required('medecin', 'administrateur')
def consultation_create_view(request):
    """Création d'une consultation (médecin seulement - R6)."""
    patient_id = request.GET.get('patient')
    rdv_id = request.GET.get('rdv')

    initial = {}
    if patient_id:
        initial['patient'] = patient_id
    if rdv_id:
        initial['rendez_vous'] = rdv_id

    if request.method == 'POST':
        form = ConsultationForm(request.POST, medecin=request.user)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.medecin = request.user
            consultation.save()

            # Si lié à un RDV, marquer comme effectué
            if consultation.rendez_vous:
                consultation.rendez_vous.statut = 'effectue'
                consultation.rendez_vous.save(update_fields=['statut'])

            log_action(
                user=request.user,
                action='CREATE',
                entity='Consultation',
                entity_id=str(consultation.pk),
                after={
                    'patient': consultation.patient.nom_complet,
                    'statut': consultation.statut,
                    'date': str(consultation.date_heure),
                },
                request=request
            )
            messages.success(request, "Consultation créée.")
            return redirect('consultations:detail', pk=consultation.pk)
        else:
            messages.error(request, "Erreur lors de la création de la consultation.")
    else:
        form = ConsultationForm(initial=initial, medecin=request.user)

    return render(request, 'consultations/form.html', {
        'form': form,
        'action': 'Nouvelle consultation'
    })


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def consultation_detail_view(request, pk):
    """Détail d'une consultation."""
    consultation = get_object_or_404(
        Consultation.objects.select_related('patient', 'medecin', 'rendez_vous'),
        pk=pk
    )

    # Alertes tension oculaire
    alertes = []
    if consultation.tension_od_anormale:
        alertes.append({
            'type': 'danger',
            'message': f"Tension OD anormale: {consultation.tension_od} mmHg (norme: 10-21 mmHg)"
        })
    if consultation.tension_og_anormale:
        alertes.append({
            'type': 'danger',
            'message': f"Tension OG anormale: {consultation.tension_og} mmHg (norme: 10-21 mmHg)"
        })
    if consultation.patient.has_allergies:
        alertes.append({
            'type': 'warning',
            'message': f"Allergies connues: {consultation.patient.allergies}"
        })

    # Historique pour graphiques
    historique = Consultation.objects.filter(
        patient=consultation.patient,
        statut__in=['valide', 'brouillon']
    ).order_by('date_heure').values(
        'date_heure', 'tension_od', 'tension_og',
        'acuite_od_loin', 'acuite_og_loin'
    )

    is_partial_view = request.user.is_secretaire

    return render(request, 'consultations/detail.html', {
        'consultation': consultation,
        'alertes': alertes,
        'historique_json': json.dumps(list(historique), default=str),
        'is_partial_view': is_partial_view,
    })


@login_required
@role_required('medecin', 'administrateur')
def consultation_edit_view(request, pk):
    """Modification d'une consultation en brouillon (R6, R7)."""
    consultation = get_object_or_404(Consultation, pk=pk)

    if not consultation.peut_etre_modifiee:
        messages.error(request, "Cette consultation est validée et ne peut plus être modifiée.")
        return redirect('consultations:detail', pk=pk)

    before_data = {
        'statut': consultation.statut,
        'diagnostic_principal': consultation.diagnostic_principal,
        'tension_od': str(consultation.tension_od),
        'tension_og': str(consultation.tension_og),
    }

    if request.method == 'POST':
        form = ConsultationForm(request.POST, instance=consultation, medecin=request.user)
        if form.is_valid():
            consultation = form.save()
            log_action(
                user=request.user,
                action='UPDATE',
                entity='Consultation',
                entity_id=str(consultation.pk),
                before=before_data,
                after={
                    'statut': consultation.statut,
                    'diagnostic_principal': consultation.diagnostic_principal,
                },
                request=request
            )
            messages.success(request, "Consultation modifiée.")
            return redirect('consultations:detail', pk=consultation.pk)
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = ConsultationForm(instance=consultation, medecin=request.user)

    return render(request, 'consultations/form.html', {
        'form': form,
        'action': 'Modifier la consultation',
        'consultation': consultation
    })


@login_required
@role_required('medecin', 'administrateur')
def consultation_validate_view(request, pk):
    """Validation d'une consultation (R7)."""
    consultation = get_object_or_404(Consultation, pk=pk)

    if request.method == 'POST':
        if consultation.statut != 'brouillon':
            messages.error(request, "Seule une consultation en brouillon peut être validée.")
            return redirect('consultations:detail', pk=pk)

        consultation.valider()
        log_action(
            user=request.user,
            action='UPDATE',
            entity='Consultation',
            entity_id=str(consultation.pk),
            before={'statut': 'brouillon'},
            after={'statut': 'valide', 'date_validation': str(consultation.date_validation)},
            request=request
        )
        messages.success(request, "Consultation validée. Elle ne peut plus être modifiée.")
        return redirect('consultations:detail', pk=pk)

    return render(request, 'consultations/confirm_validate.html', {'consultation': consultation})


@login_required
@role_required('medecin', 'administrateur')
def consultation_cancel_view(request, pk):
    """Annulation d'une consultation avec motif obligatoire (R7)."""
    consultation = get_object_or_404(Consultation, pk=pk)

    if consultation.statut == 'annule':
        messages.info(request, "Cette consultation est déjà annulée.")
        return redirect('consultations:detail', pk=pk)

    if request.method == 'POST':
        form = ConsultationCancelForm(request.POST)
        if form.is_valid():
            motif = form.cleaned_data['motif_annulation']
            before_statut = consultation.statut
            consultation.annuler(motif)
            log_action(
                user=request.user,
                action='UPDATE',
                entity='Consultation',
                entity_id=str(consultation.pk),
                before={'statut': before_statut},
                after={'statut': 'annule', 'motif': motif},
                request=request
            )
            messages.success(request, "Consultation annulée.")
            return redirect('consultations:detail', pk=pk)
    else:
        form = ConsultationCancelForm()

    return render(request, 'consultations/cancel_form.html', {
        'form': form,
        'consultation': consultation
    })


@login_required
@role_required('medecin', 'administrateur')
def consultation_history_api(request, patient_id):
    """API: historique des consultations pour graphiques Chart.js."""
    from apps.patients.models import Patient
    patient = get_object_or_404(Patient, pk=patient_id)

    consultations = Consultation.objects.filter(
        patient=patient,
        statut__in=['valide', 'brouillon']
    ).order_by('date_heure').values(
        'date_heure', 'tension_od', 'tension_og',
        'acuite_od_loin', 'acuite_og_loin', 'pk'
    )

    data = []
    for c in consultations:
        data.append({
            'date': c['date_heure'].strftime('%d/%m/%Y') if c['date_heure'] else '',
            'tension_od': float(c['tension_od']) if c['tension_od'] else None,
            'tension_og': float(c['tension_og']) if c['tension_og'] else None,
            'acuite_od': c['acuite_od_loin'],
            'acuite_og': c['acuite_og_loin'],
            'id': c['pk'],
        })

    return JsonResponse({'data': data, 'patient': patient.nom_complet})
