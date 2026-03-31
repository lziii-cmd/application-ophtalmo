"""
Vues pour la gestion des patients.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator

from .models import Patient
from .forms import PatientForm, PatientSearchForm
from apps.accounts.decorators import role_required, medecin_required
from apps.audit.utils import log_action


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def patient_list_view(request):
    """Liste et recherche de patients."""
    form = PatientSearchForm(request.GET)
    patients = Patient.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get('q', '').strip()
        statut = form.cleaned_data.get('statut', '')

        if q:
            patients = patients.filter(
                Q(nom__icontains=q) |
                Q(prenom__icontains=q) |
                Q(telephone__icontains=q) |
                Q(pk__icontains=q)
            )

        if statut:
            patients = patients.filter(statut=statut)
        else:
            # Par défaut, afficher seulement les actifs
            patients = patients.filter(statut='actif')
    else:
        patients = patients.filter(statut='actif')

    patients = patients.order_by('nom', 'prenom')
    paginator = Paginator(patients, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'patients/list.html', {
        'form': form,
        'page_obj': page_obj,
        'total_count': patients.count(),
    })


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def patient_detail_view(request, pk):
    """Détail d'un patient avec tout son historique."""
    patient = get_object_or_404(Patient, pk=pk)

    log_action(
        user=request.user,
        action='READ',
        entity='Patient',
        entity_id=str(patient.pk),
        after={'patient': patient.nom_complet},
        request=request
    )

    consultations = patient.consultations.all().order_by('-date_heure')
    paiements = patient.paiements.all().order_by('-date')
    rendez_vous = patient.rendez_vous.all().order_by('-date_heure')
    prescriptions = []
    for c in consultations:
        prescriptions.extend(list(c.prescriptions.all()))

    # Alertes patient
    alertes = []
    if patient.has_allergies:
        alertes.append({
            'type': 'warning',
            'message': f"Allergies connues: {patient.allergies}"
        })
    if patient.a_recontacter:
        alertes.append({
            'type': 'info',
            'message': "Patient à recontacter - Pas de consultation depuis plus de 12 mois"
        })

    return render(request, 'patients/detail.html', {
        'patient': patient,
        'consultations': consultations,
        'paiements': paiements,
        'rendez_vous': rendez_vous,
        'prescriptions': prescriptions,
        'alertes': alertes,
    })


@login_required
@role_required('secretaire', 'administrateur')
def patient_create_view(request):
    """Création d'un nouveau patient."""
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            log_action(
                user=request.user,
                action='CREATE',
                entity='Patient',
                entity_id=str(patient.pk),
                after={
                    'nom': patient.nom,
                    'prenom': patient.prenom,
                    'date_naissance': str(patient.date_naissance),
                },
                request=request
            )
            messages.success(request, f"Patient {patient.nom_complet} créé avec succès.")
            return redirect('patients:detail', pk=patient.pk)
        else:
            messages.error(request, "Erreur lors de la création du patient. Vérifiez les champs.")
    else:
        form = PatientForm()

    return render(request, 'patients/form.html', {'form': form, 'action': 'Nouveau patient'})


@login_required
@role_required('secretaire', 'administrateur')
def patient_edit_view(request, pk):
    """Modification d'un patient."""
    patient = get_object_or_404(Patient, pk=pk)
    before_data = {
        'nom': patient.nom,
        'prenom': patient.prenom,
        'telephone': patient.telephone,
        'adresse': patient.adresse,
        'allergies': patient.allergies,
        'traitements_en_cours': patient.traitements_en_cours,
    }

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save()
            log_action(
                user=request.user,
                action='UPDATE',
                entity='Patient',
                entity_id=str(patient.pk),
                before=before_data,
                after={
                    'nom': patient.nom,
                    'prenom': patient.prenom,
                    'telephone': patient.telephone,
                },
                request=request
            )
            messages.success(request, f"Patient {patient.nom_complet} modifié avec succès.")
            return redirect('patients:detail', pk=patient.pk)
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = PatientForm(instance=patient)

    return render(request, 'patients/form.html', {
        'form': form,
        'action': f'Modifier - {patient.nom_complet}',
        'patient': patient
    })


@login_required
@role_required('administrateur')
def patient_archive_view(request, pk):
    """Archivage logique d'un patient (pas de suppression physique - R2)."""
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        patient.archiver()
        log_action(
            user=request.user,
            action='UPDATE',
            entity='Patient',
            entity_id=str(patient.pk),
            before={'statut': 'actif'},
            after={'statut': 'archive'},
            request=request
        )
        messages.success(request, f"Patient {patient.nom_complet} archivé.")
        return redirect('patients:list')

    return render(request, 'patients/confirm_archive.html', {'patient': patient})


@login_required
@role_required('administrateur')
def patient_reactivate_view(request, pk):
    """Réactivation d'un patient archivé."""
    patient = get_object_or_404(Patient, pk=pk)
    patient.reactiver()
    log_action(
        user=request.user,
        action='UPDATE',
        entity='Patient',
        entity_id=str(patient.pk),
        before={'statut': 'archive'},
        after={'statut': 'actif'},
        request=request
    )
    messages.success(request, f"Patient {patient.nom_complet} réactivé.")
    return redirect('patients:detail', pk=patient.pk)


@login_required
@role_required('medecin', 'administrateur')
def patient_export_pdf_view(request, pk):
    """Export du dossier patient en PDF."""
    from apps.prescriptions.pdf import generate_patient_record_pdf
    patient = get_object_or_404(Patient, pk=pk)
    return generate_patient_record_pdf(patient)


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def patient_search_api(request):
    """API de recherche de patients (AJAX)."""
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    patients = Patient.objects.filter(
        Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(telephone__icontains=q),
        statut='actif'
    )[:10]

    results = [{
        'id': p.pk,
        'text': f"{p.nom_complet} - {p.date_naissance.strftime('%d/%m/%Y')} - Tél: {p.telephone}",
        'nom': p.nom,
        'prenom': p.prenom,
    } for p in patients]

    return JsonResponse({'results': results})
