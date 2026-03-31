"""
Vues pour les paiements.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Q
from decimal import Decimal

from .models import Paiement
from .forms import PaiementForm
from apps.accounts.decorators import role_required, admin_required
from apps.patients.models import Patient
from apps.consultations.models import Consultation
from apps.audit.utils import log_action


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def paiement_list_view(request):
    """Liste des paiements avec filtres."""
    paiements = Paiement.objects.select_related('patient', 'consultation', 'created_by')

    # Filtres
    patient_id = request.GET.get('patient', '')
    statut_filtre = request.GET.get('statut', '')
    type_filtre = request.GET.get('type', '')

    if patient_id:
        paiements = paiements.filter(patient_id=patient_id)
    if type_filtre:
        paiements = paiements.filter(type_paiement=type_filtre)

    paiements = paiements.order_by('-date', '-date_creation')[:100]

    # Totaux
    total_montant = paiements.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')

    return render(request, 'paiements/list.html', {
        'paiements': paiements,
        'total_montant': total_montant,
        'patient_id': patient_id,
    })


@login_required
@role_required('secretaire', 'administrateur')
def paiement_create_view(request):
    """Enregistrement d'un nouveau paiement."""
    patient_id = request.GET.get('patient') or request.POST.get('patient')
    consultation_id = request.GET.get('consultation')

    initial = {}
    if patient_id:
        initial['patient'] = patient_id
    if consultation_id:
        initial['consultation'] = consultation_id
        try:
            consult = Consultation.objects.get(pk=consultation_id)
            initial['type_paiement'] = 'consultation'
        except Consultation.DoesNotExist:
            pass

    if request.method == 'POST':
        form = PaiementForm(request.POST, patient_id=request.POST.get('patient'))
        if form.is_valid():
            paiement = form.save(commit=False)
            paiement.created_by = request.user
            paiement.save()
            log_action(
                user=request.user,
                action='CREATE',
                entity='Paiement',
                entity_id=str(paiement.pk),
                after={
                    'patient': paiement.patient.nom_complet,
                    'montant': str(paiement.montant),
                    'type': paiement.type_paiement,
                    'mode': paiement.mode_paiement,
                },
                request=request
            )
            messages.success(request, f"Paiement de {paiement.montant}€ enregistré pour {paiement.patient.nom_complet}.")
            return redirect('paiements:list')
        else:
            messages.error(request, "Erreur lors de l'enregistrement du paiement.")
    else:
        form = PaiementForm(initial=initial, patient_id=patient_id)

    return render(request, 'paiements/form.html', {
        'form': form,
        'action': 'Nouveau paiement'
    })


@login_required
@role_required('secretaire', 'administrateur')
def paiement_edit_view(request, pk):
    """Modification d'un paiement. Admin requis si paiement validé (R12)."""
    paiement = get_object_or_404(Paiement, pk=pk)

    # R12: modification paiement validé nécessite admin
    if paiement.valide and not request.user.is_administrateur and not request.user.is_superuser:
        messages.error(request, "Ce paiement est validé. Seul l'administrateur peut le modifier (R12).")
        return redirect('paiements:list')

    before_data = {
        'montant': str(paiement.montant),
        'type_paiement': paiement.type_paiement,
        'mode_paiement': paiement.mode_paiement,
        'valide': paiement.valide,
    }

    if request.method == 'POST':
        form = PaiementForm(request.POST, instance=paiement, patient_id=paiement.patient_id)
        if form.is_valid():
            paiement = form.save()
            log_action(
                user=request.user,
                action='UPDATE',
                entity='Paiement',
                entity_id=str(paiement.pk),
                before=before_data,
                after={
                    'montant': str(paiement.montant),
                    'type_paiement': paiement.type_paiement,
                    'mode_paiement': paiement.mode_paiement,
                },
                request=request
            )
            messages.success(request, "Paiement modifié.")
            return redirect('paiements:list')
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = PaiementForm(instance=paiement, patient_id=paiement.patient_id)

    return render(request, 'paiements/form.html', {
        'form': form,
        'action': 'Modifier le paiement',
        'paiement': paiement
    })


@login_required
@admin_required
def paiement_validate_view(request, pk):
    """Validation d'un paiement (admin)."""
    paiement = get_object_or_404(Paiement, pk=pk)
    if request.method == 'POST':
        paiement.valide = True
        paiement.save(update_fields=['valide', 'date_modification'])
        log_action(
            user=request.user,
            action='UPDATE',
            entity='Paiement',
            entity_id=str(paiement.pk),
            before={'valide': False},
            after={'valide': True},
            request=request
        )
        messages.success(request, "Paiement validé.")
    return redirect('paiements:list')


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def paiement_patient_view(request, patient_pk):
    """Historique des paiements d'un patient."""
    patient = get_object_or_404(Patient, pk=patient_pk)
    paiements = Paiement.objects.filter(patient=patient).order_by('-date')

    total_paye = paiements.aggregate(total=Sum('montant'))['total'] or Decimal('0.00')

    return render(request, 'paiements/list.html', {
        'paiements': paiements,
        'patient': patient,
        'total_montant': total_paye,
    })


@login_required
@role_required('secretaire', 'administrateur')
def get_consultations_for_patient(request):
    """API AJAX: récupère les consultations pour un patient donné."""
    patient_id = request.GET.get('patient_id')
    if not patient_id:
        return JsonResponse({'consultations': []})

    consultations = Consultation.objects.filter(
        patient_id=patient_id,
        statut__in=['valide', 'brouillon']
    ).order_by('-date_heure').values('pk', 'date_heure', 'diagnostic_principal')

    data = [{
        'id': c['pk'],
        'text': f"Consultation du {c['date_heure'].strftime('%d/%m/%Y')} - {c['diagnostic_principal'][:50] if c['diagnostic_principal'] else 'Sans diagnostic'}",
    } for c in consultations]

    return JsonResponse({'consultations': data})
