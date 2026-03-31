"""
Context processors pour les notifications globales.
"""

from django.utils import timezone
from datetime import timedelta
from decimal import Decimal


def notifications_processor(request):
    """
    Ajoute les alertes et notifications au contexte global.
    """
    if not request.user.is_authenticated:
        return {}

    notifications = []

    try:
        # Alertes selon le rôle
        if request.user.is_medecin or request.user.is_superuser or request.user.is_administrateur:
            # Alertes pour le médecin et admin
            from apps.patients.models import Patient

            # Patients à recontacter (médecin et admin)
            patients_a_recontacter = sum(
                1 for p in Patient.objects.filter(statut='actif')[:100]
                if p.a_recontacter
            )
            if patients_a_recontacter > 0:
                notifications.append({
                    'type': 'info',
                    'icon': 'bi-person-exclamation',
                    'message': f"{patients_a_recontacter} patient(s) à recontacter (>12 mois sans consultation)",
                    'url': '/patients/?statut=actif',
                })

        if request.user.is_secretaire or request.user.is_superuser or request.user.is_administrateur:
            # Alertes pour la secrétaire et admin
            from apps.paiements.models import Paiement
            from django.db.models import Sum

            today = timezone.now().date()
            date_limite = today - timedelta(days=30)

            # Paiements impayés > 30 jours
            paiements_anciens = Paiement.objects.filter(
                date__lte=date_limite,
                montant_total_du__gt=Decimal('0.00')
            )
            nb_impayes = sum(1 for p in paiements_anciens[:50] if p.statut_calcule == 'non_paye')
            if nb_impayes > 0:
                notifications.append({
                    'type': 'warning',
                    'icon': 'bi-exclamation-triangle',
                    'message': f"{nb_impayes} consultation(s) impayée(s) depuis plus de 30 jours",
                    'url': '/paiements/',
                })

        if request.user.is_administrateur or request.user.is_superuser:
            # Alertes admin uniquement
            from apps.sauvegarde.models import Sauvegarde
            from apps.accounts.models import CustomUser

            # Sauvegardes en échec
            nb_echecs = Sauvegarde.objects.filter(statut='echec').count()
            if nb_echecs > 0:
                notifications.append({
                    'type': 'danger',
                    'icon': 'bi-database-x',
                    'message': f"{nb_echecs} sauvegarde(s) en échec",
                    'url': '/sauvegarde/',
                })

            # Comptes verrouillés
            now = timezone.now()
            comptes_verrouillis = CustomUser.objects.filter(locked_until__gt=now).count()
            if comptes_verrouillis > 0:
                notifications.append({
                    'type': 'warning',
                    'icon': 'bi-lock',
                    'message': f"{comptes_verrouillis} compte(s) verrouillé(s)",
                    'url': '/accounts/utilisateurs/',
                })

    except Exception:
        pass  # Ne jamais bloquer sur les notifications

    return {
        'global_notifications': notifications,
        'notification_count': len(notifications),
    }
