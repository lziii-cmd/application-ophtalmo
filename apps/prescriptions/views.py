"""
Vues pour les prescriptions médicales.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Prescription
from .forms import (
    PrescriptionLunettesForm,
    PrescriptionTraitementForm,
    PrescriptionExamenForm,
    PrescriptionLentillesForm,
)
from .pdf import generate_prescription_pdf
from apps.consultations.models import Consultation
from apps.accounts.decorators import role_required, medecin_required
from apps.audit.utils import log_action

FORM_MAP = {
    'lunettes': PrescriptionLunettesForm,
    'traitement': PrescriptionTraitementForm,
    'examen': PrescriptionExamenForm,
    'lentilles': PrescriptionLentillesForm,
}


@login_required
@role_required('medecin', 'administrateur')
def prescription_list_view(request):
    """Liste de toutes les prescriptions."""
    from django.core.paginator import Paginator
    prescriptions = Prescription.objects.select_related(
        'consultation__patient', 'medecin'
    ).order_by('-date_creation')

    type_filter = request.GET.get('type', '')
    if type_filter:
        prescriptions = prescriptions.filter(type_prescription=type_filter)

    paginator = Paginator(prescriptions, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'prescriptions/list.html', {
        'page_obj': page_obj,
        'type_filter': type_filter,
    })


@login_required
@role_required('medecin', 'administrateur')
def prescription_create_view(request, consultation_pk):
    """Création d'une prescription liée à une consultation (R8)."""
    consultation = get_object_or_404(Consultation, pk=consultation_pk)
    type_prescription = request.GET.get('type', 'lunettes')

    if type_prescription not in FORM_MAP:
        type_prescription = 'lunettes'

    FormClass = FORM_MAP[type_prescription]

    if request.method == 'POST':
        type_from_post = request.POST.get('type_prescription', type_prescription)
        if type_from_post in FORM_MAP:
            type_prescription = type_from_post
            FormClass = FORM_MAP[type_prescription]

        form = FormClass(request.POST)
        if form.is_valid():
            contenu = form.to_contenu()
            prescription = Prescription.objects.create(
                consultation=consultation,
                medecin=request.user,
                type_prescription=type_prescription,
                contenu=contenu,
            )
            log_action(
                user=request.user,
                action='CREATE',
                entity='Prescription',
                entity_id=str(prescription.pk),
                after={
                    'type': type_prescription,
                    'patient': consultation.patient.nom_complet,
                    'consultation_id': consultation.pk,
                },
                request=request
            )
            messages.success(request, f"Prescription ({prescription.get_type_prescription_display()}) créée.")
            return redirect('prescriptions:detail', pk=prescription.pk)
        else:
            messages.error(request, "Erreur lors de la création de la prescription.")
    else:
        form = FormClass()

    type_labels = {
        'lunettes': 'Ordonnance lunettes',
        'traitement': 'Traitement médical',
        'examen': 'Examens complémentaires',
        'lentilles': 'Lentilles de contact',
    }

    return render(request, 'prescriptions/form.html', {
        'form': form,
        'consultation': consultation,
        'type_prescription': type_prescription,
        'type_label': type_labels.get(type_prescription, ''),
        'type_labels': type_labels,
    })


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def prescription_detail_view(request, pk):
    """Détail d'une prescription."""
    prescription = get_object_or_404(
        Prescription.objects.select_related('consultation__patient', 'medecin'),
        pk=pk
    )
    return render(request, 'prescriptions/detail.html', {'prescription': prescription})


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def prescription_pdf_view(request, pk):
    """Génération et téléchargement du PDF d'une prescription."""
    prescription = get_object_or_404(
        Prescription.objects.select_related('consultation__patient', 'medecin'),
        pk=pk
    )
    log_action(
        user=request.user,
        action='READ',
        entity='Prescription',
        entity_id=str(prescription.pk),
        after={'action': 'pdf_generated'},
        request=request
    )
    return generate_prescription_pdf(prescription)
