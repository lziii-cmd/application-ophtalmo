"""
Vues pour le module chirurgie ophtalmologique.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q

from apps.accounts.decorators import role_required
from .models import Intervention, SuiviPostOp
from .forms import InterventionForm, CompteRenduForm, SuiviPostOpForm


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def intervention_list_view(request):
    interventions = Intervention.objects.select_related('patient', 'chirurgien').all()

    statut = request.GET.get('statut', '')
    type_filter = request.GET.get('type', '')
    q = request.GET.get('q', '').strip()

    if statut:
        interventions = interventions.filter(statut=statut)
    if type_filter:
        interventions = interventions.filter(type_intervention=type_filter)
    if q:
        interventions = interventions.filter(
            Q(patient__nom__icontains=q) | Q(patient__prenom__icontains=q)
        )

    context = {
        'interventions': interventions,
        'statut_filter': statut,
        'type_filter': type_filter,
        'q': q,
        'type_choices': Intervention.TYPE_CHOICES,
        'statut_choices': Intervention.STATUT_CHOICES,
        'nb_planifiees': Intervention.objects.filter(statut='planifiee').count(),
        'nb_realisees': Intervention.objects.filter(statut='realisee').count(),
        'nb_ce_mois': Intervention.objects.filter(
            date_planifiee__month=timezone.now().month,
            date_planifiee__year=timezone.now().year,
        ).count(),
    }
    return render(request, 'chirurgie/list.html', context)


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def intervention_detail_view(request, pk):
    intervention = get_object_or_404(
        Intervention.objects.select_related('patient', 'chirurgien', 'rdv_operation'),
        pk=pk
    )
    suivis = intervention.suivis.select_related('rdv', 'medecin').all()

    context = {
        'intervention': intervention,
        'suivis': suivis,
    }
    return render(request, 'chirurgie/detail.html', context)


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def intervention_create_view(request):
    from apps.accounts.models import CustomUser
    from apps.patients.models import Patient

    initial = {}
    patient_pk = request.GET.get('patient')
    if patient_pk:
        initial['patient'] = patient_pk

    if request.method == 'POST':
        form = InterventionForm(request.POST)
        if form.is_valid():
            intervention = form.save(commit=False)
            intervention.created_by = request.user
            intervention.save()
            messages.success(request, "Intervention planifiée avec succès.")
            return redirect('chirurgie:detail', intervention.pk)
    else:
        form = InterventionForm(initial=initial)
        # Limiter chirurgiens aux médecins
        form.fields['chirurgien'].queryset = CustomUser.objects.filter(role='medecin', is_active=True)
        if request.user.is_medecin:
            form.fields['chirurgien'].initial = request.user

    return render(request, 'chirurgie/form.html', {'form': form, 'titre': 'Planifier une intervention'})


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def intervention_edit_view(request, pk):
    from apps.accounts.models import CustomUser
    intervention = get_object_or_404(Intervention, pk=pk)

    if request.method == 'POST':
        form = InterventionForm(request.POST, instance=intervention)
        if form.is_valid():
            form.save()
            messages.success(request, "Intervention mise à jour.")
            return redirect('chirurgie:detail', pk)
    else:
        form = InterventionForm(instance=intervention)
        form.fields['chirurgien'].queryset = CustomUser.objects.filter(role='medecin', is_active=True)

    return render(request, 'chirurgie/form.html', {'form': form, 'titre': 'Modifier l\'intervention', 'intervention': intervention})


@login_required
@role_required('medecin')
def compte_rendu_view(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk)

    if request.method == 'POST':
        form = CompteRenduForm(request.POST, instance=intervention)
        if form.is_valid():
            intervention = form.save(commit=False)
            intervention.statut = 'realisee'
            intervention.save()
            # Créer automatiquement les suivis post-op
            _creer_suivis_auto(intervention)
            messages.success(request, "Compte-rendu enregistré. Suivis post-op créés automatiquement.")
            return redirect('chirurgie:detail', pk)
    else:
        form = CompteRenduForm(instance=intervention)

    return render(request, 'chirurgie/compte_rendu.html', {'form': form, 'intervention': intervention})


@login_required
@role_required('medecin')
def suivi_create_view(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk)

    if request.method == 'POST':
        form = SuiviPostOpForm(request.POST)
        if form.is_valid():
            suivi = form.save(commit=False)
            suivi.intervention = intervention
            suivi.medecin = request.user
            suivi.save()
            messages.success(request, "Suivi post-opératoire enregistré.")
            return redirect('chirurgie:detail', pk)
    else:
        form = SuiviPostOpForm()

    return render(request, 'chirurgie/suivi_form.html', {'form': form, 'intervention': intervention})


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def intervention_valider_pre_op(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk)
    if request.method == 'POST':
        intervention.statut = 'pre_op_valide'
        intervention.save()
        messages.success(request, "Bilan pré-opératoire validé.")
    return redirect('chirurgie:detail', pk)


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def intervention_annuler(request, pk):
    intervention = get_object_or_404(Intervention, pk=pk)
    if request.method == 'POST':
        intervention.statut = 'annulee'
        intervention.save()
        messages.warning(request, "Intervention annulée.")
    return redirect('chirurgie:detail', pk)


def _creer_suivis_auto(intervention):
    """Crée automatiquement les rendez-vous de suivi J+1, J+7, J+30 après l'opération."""
    from datetime import timedelta
    if not intervention.date_realisation:
        return
    date_op = intervention.date_realisation.date()
    suivis = [
        ('j1', date_op + timedelta(days=1)),
        ('j7', date_op + timedelta(days=7)),
        ('j30', date_op + timedelta(days=30)),
    ]
    for type_suivi, date_prevue in suivis:
        SuiviPostOp.objects.get_or_create(
            intervention=intervention,
            type_suivi=type_suivi,
            defaults={'date_prevue': date_prevue}
        )
