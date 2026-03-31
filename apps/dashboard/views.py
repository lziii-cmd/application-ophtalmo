"""
Vues pour le tableau de bord principal.
"""

import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal

from apps.accounts.decorators import role_required


@login_required
def dashboard_index_view(request):
    """
    Tableau de bord principal avec indicateurs adaptés au rôle.
    """
    user = request.user
    today = timezone.now().date()
    now = timezone.now()

    context = {
        'today': today,
        'user': user,
    }

    try:
        from apps.patients.models import Patient
        from apps.agenda.models import RendezVous
        from apps.consultations.models import Consultation
        from apps.paiements.models import Paiement
        from django.db.models import Sum, Q, Count

        if user.is_medecin or user.is_superuser:
            # Indicateurs pour le médecin
            prochain_rdv = RendezVous.objects.filter(
                medecin=user if user.is_medecin else None,
                date_heure__gte=now,
                statut='programme'
            ).order_by('date_heure').first() if user.is_medecin else RendezVous.objects.filter(
                date_heure__gte=now,
                statut='programme'
            ).order_by('date_heure').first()

            consultations_jour = Consultation.objects.filter(
                date_heure__date=today,
                medecin=user if user.is_medecin else None,
            ).count() if user.is_medecin else Consultation.objects.filter(
                date_heure__date=today
            ).count()

            rdv_jour = RendezVous.objects.filter(
                date_heure__date=today,
                medecin=user if user.is_medecin else None,
                statut__in=['programme', 'effectue'],
            ).count() if user.is_medecin else RendezVous.objects.filter(
                date_heure__date=today,
                statut__in=['programme', 'effectue'],
            ).count()

            # Patients à recontacter (pas de consultation depuis 12 mois)
            date_limite = now - timedelta(days=365)
            patients_actifs = Patient.objects.filter(statut='actif')
            patients_a_recontacter = []
            for p in patients_actifs[:200]:  # Limiter pour performance
                if p.a_recontacter:
                    patients_a_recontacter.append(p)
            nb_patients_a_recontacter = len(patients_a_recontacter)

            context.update({
                'prochain_rdv': prochain_rdv,
                'consultations_jour': consultations_jour,
                'rdv_jour': rdv_jour,
                'nb_patients_a_recontacter': nb_patients_a_recontacter,
                'patients_a_recontacter_liste': patients_a_recontacter[:5],
            })

        if user.is_secretaire or user.is_superuser:
            # Indicateurs pour la secrétaire
            patients_actifs_count = Patient.objects.filter(statut='actif').count()
            consultations_jour_total = Consultation.objects.filter(date_heure__date=today).count()
            rdv_jour_total = RendezVous.objects.filter(
                date_heure__date=today,
                statut__in=['programme', 'effectue']
            ).count()

            # Encaissements du jour
            encaissement_jour = Paiement.objects.filter(
                date=today
            ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')

            # Consultations impayées > 30 jours
            date_limite_impaye = today - timedelta(days=30)
            impayes = Paiement.objects.filter(
                date__lte=date_limite_impaye,
                montant_total_du__gt=Decimal('0.00'),
            )
            nb_impayes = sum(1 for p in impayes if p.statut_calcule == 'non_paye')

            context.update({
                'patients_actifs_count': patients_actifs_count,
                'consultations_jour_total': consultations_jour_total,
                'rdv_jour_total': rdv_jour_total,
                'encaissement_jour': encaissement_jour,
                'nb_impayes': nb_impayes,
            })

        if user.is_administrateur or user.is_superuser:
            # Indicateurs pour l'administrateur
            from apps.accounts.models import CustomUser
            from apps.sauvegarde.models import Sauvegarde

            total_patients = Patient.objects.count()
            total_consultations = Consultation.objects.count()
            total_utilisateurs = CustomUser.objects.filter(is_active=True).count()

            # Dernière sauvegarde
            derniere_sauvegarde = Sauvegarde.objects.filter(statut='reussie').first()

            # Comptes verrouillés
            from django.db.models import Q as DQ
            now_dt = timezone.now()
            comptes_verrouillis = CustomUser.objects.filter(
                locked_until__gt=now_dt
            ).count()

            # Stats sauvegardes
            sauvegardes_echec = Sauvegarde.objects.filter(statut='echec').count()

            context.update({
                'total_patients': total_patients,
                'total_consultations': total_consultations,
                'total_utilisateurs': total_utilisateurs,
                'derniere_sauvegarde': derniere_sauvegarde,
                'comptes_verrouillis': comptes_verrouillis,
                'sauvegardes_echec': sauvegardes_echec,
            })

        # Rendez-vous du jour pour tous
        rdv_aujourd_hui = RendezVous.objects.filter(
            date_heure__date=today,
            statut='programme'
        ).select_related('patient', 'medecin').order_by('date_heure')[:10]

        if user.is_medecin:
            rdv_aujourd_hui = rdv_aujourd_hui.filter(medecin=user)

        context['rdv_aujourd_hui'] = rdv_aujourd_hui

        # Données graphique : consultations par mois sur 6 mois
        mois_labels = []
        mois_consultations = []
        mois_rdv = []
        for i in range(5, -1, -1):
            # Calcul propre du 1er du mois i mois en arrière
            month = today.month - i
            year = today.year
            while month <= 0:
                month += 12
                year -= 1
            debut = today.replace(year=year, month=month, day=1)
            if debut.month == 12:
                fin = debut.replace(year=debut.year + 1, month=1, day=1)
            else:
                fin = debut.replace(month=debut.month + 1, day=1)
            nb_consult = Consultation.objects.filter(
                date_heure__date__gte=debut,
                date_heure__date__lt=fin,
            ).count()
            nb_rdv = RendezVous.objects.filter(
                date_heure__date__gte=debut,
                date_heure__date__lt=fin,
            ).count()
            mois_labels.append(debut.strftime('%b %Y'))
            mois_consultations.append(nb_consult)
            mois_rdv.append(nb_rdv)

        # Répartition patients par sexe
        from apps.patients.models import Patient as PatientModel
        nb_homme = PatientModel.objects.filter(sexe='M', statut='actif').count()
        nb_femme = PatientModel.objects.filter(sexe='F', statut='actif').count()

        context['chart_labels'] = json.dumps(mois_labels)
        context['chart_consultations'] = json.dumps(mois_consultations)
        context['chart_rdv'] = json.dumps(mois_rdv)
        context['chart_sexe'] = json.dumps([nb_homme, nb_femme])

    except Exception as e:
        import logging
        logging.getLogger('apps.dashboard').error(f"Erreur dashboard: {e}", exc_info=True)
        context['dashboard_error'] = str(e)

    return render(request, 'dashboard/index.html', context)
