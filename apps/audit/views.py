"""
Vues pour le journal d'audit.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from .models import AuditLog
from apps.accounts.decorators import admin_required


@login_required
@admin_required
def audit_list_view(request):
    """Liste du journal d'audit (admin seulement - R14)."""
    logs = AuditLog.objects.select_related('utilisateur').all()

    # Filtres
    action_filter = request.GET.get('action', '')
    entite_filter = request.GET.get('entite', '')
    user_filter = request.GET.get('user', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')

    if action_filter:
        logs = logs.filter(action=action_filter)
    if entite_filter:
        logs = logs.filter(entite__icontains=entite_filter)
    if user_filter:
        logs = logs.filter(utilisateur__username__icontains=user_filter)
    if date_debut:
        try:
            from datetime import datetime
            debut = datetime.strptime(date_debut, '%Y-%m-%d')
            logs = logs.filter(horodatage__date__gte=debut.date())
        except ValueError:
            pass
    if date_fin:
        try:
            from datetime import datetime
            fin = datetime.strptime(date_fin, '%Y-%m-%d')
            logs = logs.filter(horodatage__date__lte=fin.date())
        except ValueError:
            pass

    logs = logs.order_by('-horodatage')
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Actions disponibles pour le filtre
    action_choices = AuditLog.ACTION_CHOICES

    return render(request, 'audit/list.html', {
        'page_obj': page_obj,
        'action_choices': action_choices,
        'action_filter': action_filter,
        'entite_filter': entite_filter,
        'user_filter': user_filter,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'total_count': logs.count(),
    })
