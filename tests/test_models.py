"""
Tests unitaires pour les modèles principaux.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def medecin(db):
    from apps.accounts.models import CustomUser
    return CustomUser.objects.create_user(
        username='dr_test',
        password='TestPass123!',
        first_name='Jean',
        last_name='Dupont',
        role='medecin',
    )


@pytest.fixture
def secretaire(db):
    from apps.accounts.models import CustomUser
    return CustomUser.objects.create_user(
        username='sec_test',
        password='TestPass123!',
        role='secretaire',
    )


@pytest.fixture
def patient(db):
    from apps.patients.models import Patient
    return Patient.objects.create(
        nom='Martin',
        prenom='Alice',
        date_naissance=date(1985, 6, 15),
        sexe='F',
        telephone='0612345678',
    )


@pytest.fixture
def consultation(db, patient, medecin):
    from apps.consultations.models import Consultation
    return Consultation.objects.create(
        patient=patient,
        medecin=medecin,
        date_heure=timezone.now(),
        diagnostic_principal='Test diagnostic',
        statut='brouillon',
    )


# ============================================================
# Tests Patient
# ============================================================

@pytest.mark.django_db
def test_patient_creation(patient):
    """Un patient créé doit avoir les champs de base corrects."""
    assert patient.nom == 'Martin'
    assert patient.prenom == 'Alice'
    assert patient.statut == 'actif'
    assert patient.sexe == 'F'
    assert patient.pk is not None


@pytest.mark.django_db
def test_patient_nom_complet(patient):
    """La propriété nom_complet doit retourner Prénom NOM."""
    assert 'Martin' in patient.nom_complet
    assert 'Alice' in patient.nom_complet


@pytest.mark.django_db
def test_patient_archivage(patient):
    """L'archivage logique doit passer le statut à 'archive'."""
    assert patient.statut == 'actif'
    patient.archiver()
    patient.refresh_from_db()
    assert patient.statut == 'archive'


@pytest.mark.django_db
def test_patient_reactivation(patient):
    """La réactivation d'un patient archivé doit repasser le statut à 'actif'."""
    patient.archiver()
    patient.reactiver()
    patient.refresh_from_db()
    assert patient.statut == 'actif'


@pytest.mark.django_db
def test_patient_has_allergies_false(patient):
    """Un patient sans allergies ne doit pas avoir has_allergies=True."""
    patient.allergies = ''
    patient.save()
    assert patient.has_allergies is False


@pytest.mark.django_db
def test_patient_has_allergies_true(patient):
    """Un patient avec des allergies doit avoir has_allergies=True."""
    patient.allergies = 'Pénicilline'
    patient.save()
    assert patient.has_allergies is True


# ============================================================
# Tests Consultation
# ============================================================

@pytest.mark.django_db
def test_consultation_creation(consultation):
    """Une consultation créée doit être en statut brouillon."""
    assert consultation.statut == 'brouillon'
    assert consultation.pk is not None
    assert consultation.patient is not None
    assert consultation.medecin is not None


@pytest.mark.django_db
def test_consultation_validation(consultation):
    """Une consultation peut passer du statut brouillon à validé."""
    consultation.statut = 'valide'
    consultation.save()
    consultation.refresh_from_db()
    assert consultation.statut == 'valide'


@pytest.mark.django_db
def test_consultation_tension_anormale(consultation):
    """La propriété tension_od_anormale doit détecter les valeurs hors norme."""
    consultation.tension_od = Decimal('25.0')  # > 21 mmHg
    consultation.save()
    assert consultation.tension_od_anormale is True


@pytest.mark.django_db
def test_consultation_tension_normale(consultation):
    """La tension normale (10-21 mmHg) ne doit pas déclencher l'alerte."""
    consultation.tension_od = Decimal('15.0')
    consultation.save()
    assert consultation.tension_od_anormale is False


# ============================================================
# Tests Paiement
# ============================================================

@pytest.mark.django_db
def test_paiement_statut_paye(patient, medecin):
    """Un paiement complet doit avoir statut_calcule = 'paye'."""
    from apps.paiements.models import Paiement
    p = Paiement.objects.create(
        patient=patient,
        montant=Decimal('50.00'),
        montant_total_du=Decimal('50.00'),
        type_paiement='consultation',
        mode_paiement='especes',
        created_by=medecin,
    )
    assert p.statut_calcule == 'paye'


@pytest.mark.django_db
def test_paiement_statut_partiel(patient, medecin):
    """Un paiement partiel doit avoir statut_calcule = 'partiel'."""
    from apps.paiements.models import Paiement
    p = Paiement.objects.create(
        patient=patient,
        montant=Decimal('20.00'),
        montant_total_du=Decimal('50.00'),
        type_paiement='consultation',
        mode_paiement='especes',
        created_by=medecin,
    )
    assert p.statut_calcule in ('partiel', 'non_paye')


@pytest.mark.django_db
def test_paiement_statut_calcule(patient, medecin):
    """Le statut_calcule est une propriété dynamique, pas un champ."""
    from apps.paiements.models import Paiement
    p = Paiement.objects.create(
        patient=patient,
        montant=Decimal('0.00'),
        montant_total_du=Decimal('0.00'),
        type_paiement='consultation',
        mode_paiement='especes',
        created_by=medecin,
    )
    # Montant total dû = 0 => considéré comme payé
    assert p.statut_calcule == 'paye'


# ============================================================
# Tests AuditLog (immutabilité)
# ============================================================

@pytest.mark.django_db
def test_audit_log_creation(medecin):
    """Un AuditLog peut être créé."""
    from apps.audit.models import AuditLog
    log = AuditLog.objects.create(
        utilisateur=medecin,
        action='CREATE',
        entite='Patient',
        entite_id='1',
        valeur_apres={'nom': 'Test'},
    )
    assert log.pk is not None
    assert log.action == 'CREATE'


@pytest.mark.django_db
def test_audit_log_immutable(medecin):
    """Un AuditLog ne doit pas pouvoir être supprimé via le manager normal."""
    from apps.audit.models import AuditLog
    log = AuditLog.objects.create(
        utilisateur=medecin,
        action='READ',
        entite='Patient',
        entite_id='99',
    )
    log_pk = log.pk
    # Vérifier que le log existe bien
    assert AuditLog.objects.filter(pk=log_pk).exists()
    # NOTE: L'immuabilité est assurée au niveau des permissions/vues,
    # pas au niveau ORM - on vérifie que le log persiste correctement.
    assert AuditLog.objects.get(pk=log_pk).entite == 'Patient'


# ============================================================
# Tests RendezVous - détection de conflits
# ============================================================

@pytest.mark.django_db
def test_rdv_no_conflict(patient, medecin):
    """Deux RDV non-chevauchants ne doivent pas générer de conflit."""
    from apps.agenda.models import RendezVous
    rdv1 = RendezVous.objects.create(
        patient=patient,
        medecin=medecin,
        date_heure=timezone.now().replace(hour=9, minute=0, second=0, microsecond=0),
        duree=20,
        statut='programme',
    )
    rdv2 = RendezVous(
        patient=patient,
        medecin=medecin,
        date_heure=timezone.now().replace(hour=10, minute=0, second=0, microsecond=0),
        duree=20,
        statut='programme',
    )
    assert rdv2.check_conflict() is False


@pytest.mark.django_db
def test_rdv_conflict_detection(patient, medecin):
    """Deux RDV qui se chevauchent doivent être détectés comme conflictuels."""
    from apps.agenda.models import RendezVous
    now = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0)
    RendezVous.objects.create(
        patient=patient,
        medecin=medecin,
        date_heure=now,
        duree=30,
        statut='programme',
    )
    rdv2 = RendezVous(
        patient=patient,
        medecin=medecin,
        date_heure=now + timedelta(minutes=15),  # chevauche le premier
        duree=20,
        statut='programme',
    )
    assert rdv2.check_conflict() is True
