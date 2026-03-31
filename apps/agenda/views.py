"""
Vues pour la gestion de l'agenda et des rendez-vous.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import timedelta, datetime
import json

from .models import RendezVous
from .forms import RendezVousForm
from apps.accounts.decorators import role_required
from apps.accounts.models import CustomUser
from apps.audit.utils import log_action


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def calendar_view(request):
    """Vue calendrier hebdomadaire."""
    # Calcul de la semaine courante
    today = timezone.now().date()
    week_offset = int(request.GET.get('semaine', 0))
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)

    # Filtrage par médecin
    medecin_id = request.GET.get('medecin')
    medecins = CustomUser.objects.filter(role='medecin', is_active=True)

    rdv_qs = RendezVous.objects.filter(
        date_heure__date__gte=start_of_week,
        date_heure__date__lte=end_of_week,
    ).select_related('patient', 'medecin')

    if medecin_id:
        rdv_qs = rdv_qs.filter(medecin_id=medecin_id)
    elif request.user.is_medecin:
        rdv_qs = rdv_qs.filter(medecin=request.user)

    # Organiser par jour et heure
    days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        day_rdv = rdv_qs.filter(date_heure__date=day).order_by('date_heure')
        days.append({
            'date': day,
            'rdv': day_rdv,
            'is_today': day == today,
        })

    # Créneaux horaires (8h à 19h)
    time_slots = []
    for hour in range(8, 19):
        for minute in [0, 30]:
            time_slots.append(f"{hour:02d}:{minute:02d}")

    return render(request, 'agenda/calendar.html', {
        'days': days,
        'time_slots': time_slots,
        'start_of_week': start_of_week,
        'end_of_week': end_of_week,
        'week_offset': week_offset,
        'medecins': medecins,
        'selected_medecin_id': medecin_id,
        'today': today,
    })


@login_required
@role_required('secretaire', 'administrateur', 'medecin')
def rdv_create_view(request):
    """Création d'un rendez-vous avec vérification des conflits."""
    initial = {}
    if request.GET.get('date'):
        try:
            date_str = request.GET['date']
            initial['date_heure'] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except (ValueError, KeyError):
            pass
    if request.GET.get('patient'):
        initial['patient'] = request.GET['patient']
    if request.GET.get('medecin'):
        initial['medecin'] = request.GET['medecin']

    if request.method == 'POST':
        form = RendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)
            rdv.created_by = request.user
            rdv.save()
            log_action(
                user=request.user,
                action='CREATE',
                entity='RendezVous',
                entity_id=str(rdv.pk),
                after={
                    'patient': rdv.patient.nom_complet,
                    'medecin': rdv.medecin.get_full_name(),
                    'date_heure': str(rdv.date_heure),
                },
                request=request
            )
            messages.success(request, f"Rendez-vous créé pour {rdv.patient.nom_complet}.")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'rdv_id': rdv.pk})
            return redirect('agenda:calendar')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = RendezVousForm(initial=initial)

    return render(request, 'agenda/rdv_form.html', {'form': form, 'action': 'Nouveau rendez-vous'})


@login_required
@role_required('secretaire', 'administrateur', 'medecin')
def rdv_edit_view(request, pk):
    """Modification d'un rendez-vous."""
    rdv = get_object_or_404(RendezVous, pk=pk)
    before_data = {
        'patient': rdv.patient.nom_complet,
        'date_heure': str(rdv.date_heure),
        'statut': rdv.statut,
    }

    if request.method == 'POST':
        form = RendezVousForm(request.POST, instance=rdv)
        if form.is_valid():
            rdv = form.save()
            log_action(
                user=request.user,
                action='UPDATE',
                entity='RendezVous',
                entity_id=str(rdv.pk),
                before=before_data,
                after={
                    'patient': rdv.patient.nom_complet,
                    'date_heure': str(rdv.date_heure),
                    'statut': rdv.statut,
                },
                request=request
            )
            messages.success(request, "Rendez-vous modifié.")
            return redirect('agenda:rdv_detail', pk=rdv.pk)
        else:
            messages.error(request, "Erreur lors de la modification.")
    else:
        form = RendezVousForm(instance=rdv)

    return render(request, 'agenda/rdv_form.html', {
        'form': form,
        'action': 'Modifier le rendez-vous',
        'rdv': rdv
    })


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def rdv_detail_view(request, pk):
    """Détail d'un rendez-vous."""
    rdv = get_object_or_404(RendezVous, pk=pk)
    return render(request, 'agenda/rdv_detail.html', {'rdv': rdv})


@login_required
@role_required('secretaire', 'administrateur')
def rdv_cancel_view(request, pk):
    """Annulation d'un rendez-vous."""
    rdv = get_object_or_404(RendezVous, pk=pk)

    if request.method == 'POST':
        motif = request.POST.get('motif_annulation', '').strip()
        if not motif:
            messages.error(request, "Le motif d'annulation est obligatoire.")
            return render(request, 'agenda/rdv_cancel.html', {'rdv': rdv})

        rdv.statut = 'annule'
        rdv.motif_annulation = motif
        rdv.save()
        log_action(
            user=request.user,
            action='UPDATE',
            entity='RendezVous',
            entity_id=str(rdv.pk),
            before={'statut': 'programme'},
            after={'statut': 'annule', 'motif': motif},
            request=request
        )
        messages.success(request, "Rendez-vous annulé.")
        return redirect('agenda:calendar')

    return render(request, 'agenda/rdv_cancel.html', {'rdv': rdv})


@login_required
def calendar_events_api(request):
    """API FullCalendar - retourne les RDV au format JSON."""
    rdvs = RendezVous.objects.select_related('patient', 'medecin').all()
    start = request.GET.get('start')
    end = request.GET.get('end')
    if start:
        rdvs = rdvs.filter(date_heure__gte=start)
    if end:
        rdvs = rdvs.filter(date_heure__lte=end)

    color_map = {
        'programme': '#0d6efd',
        'effectue': '#198754',
        'annule': '#dc3545',
        'non_presente': '#ffc107',
    }
    events = []
    for rdv in rdvs:
        events.append({
            'id': rdv.pk,
            'title': str(rdv.patient.nom_complet),
            'start': rdv.date_heure.isoformat(),
            'end': rdv.heure_fin.isoformat(),
            'url': f'/agenda/{rdv.pk}/',
            'backgroundColor': color_map.get(rdv.statut, '#6c757d'),
            'borderColor': color_map.get(rdv.statut, '#6c757d'),
            'extendedProps': {
                'statut': rdv.statut,
                'motif': rdv.motif,
                'medecin': rdv.medecin.get_full_name(),
            }
        })
    return JsonResponse(events, safe=False)


@login_required
def rdv_move_api(request, pk):
    """API drag & drop - déplacer un RDV via FullCalendar."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    if not (request.user.is_secretaire or request.user.is_administrateur or request.user.is_superuser):
        return JsonResponse({'error': 'Permission refusée'}, status=403)
    try:
        rdv = RendezVous.objects.get(pk=pk)
        data = json.loads(request.body)
        new_start = data.get('start')
        from django.utils.dateparse import parse_datetime
        from django.utils import timezone as tz
        dt = parse_datetime(new_start)
        if dt and not tz.is_aware(dt):
            dt = tz.make_aware(dt)
        rdv.date_heure = dt
        rdv.save(update_fields=['date_heure'])
        log_action(
            user=request.user,
            action='UPDATE',
            entity='RendezVous',
            entity_id=str(rdv.pk),
            after={'date_heure': str(rdv.date_heure)},
            request=request
        )
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@role_required('medecin', 'secretaire', 'administrateur')
def rdv_api_events(request):
    """API pour les événements du calendrier (AJAX)."""
    start = request.GET.get('start')
    end = request.GET.get('end')
    medecin_id = request.GET.get('medecin')

    qs = RendezVous.objects.filter(
        statut__in=['programme', 'effectue']
    ).select_related('patient', 'medecin')

    if start:
        try:
            start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
            qs = qs.filter(date_heure__gte=start_dt)
        except ValueError:
            pass
    if end:
        try:
            end_dt = datetime.fromisoformat(end.replace('Z', '+00:00'))
            qs = qs.filter(date_heure__lte=end_dt)
        except ValueError:
            pass
    if medecin_id:
        qs = qs.filter(medecin_id=medecin_id)

    events = []
    for rdv in qs:
        color = '#0d6efd' if rdv.statut == 'programme' else '#198754'
        events.append({
            'id': rdv.pk,
            'title': rdv.patient.nom_complet,
            'start': rdv.date_heure.isoformat(),
            'end': rdv.heure_fin.isoformat(),
            'color': color,
            'url': f'/agenda/{rdv.pk}/',
            'extendedProps': {
                'motif': rdv.motif,
                'medecin': rdv.medecin.get_full_name(),
                'statut': rdv.get_statut_display(),
            }
        })

    return JsonResponse(events, safe=False)
