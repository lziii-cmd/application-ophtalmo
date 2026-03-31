"""
Tests de vues : authentification requise et contrôle d'accès RBAC.
"""

import pytest
from datetime import date
from django.test import Client


# ============================================================
# Fixtures
# ============================================================

@pytest.fixture
def client():
    return Client()


@pytest.fixture
def medecin(db):
    from apps.accounts.models import CustomUser
    return CustomUser.objects.create_user(
        username='dr_view_test',
        password='TestPass123!',
        first_name='Marie',
        last_name='Curie',
        role='medecin',
    )


@pytest.fixture
def secretaire(db):
    from apps.accounts.models import CustomUser
    return CustomUser.objects.create_user(
        username='sec_view_test',
        password='TestPass123!',
        role='secretaire',
    )


@pytest.fixture
def administrateur(db):
    from apps.accounts.models import CustomUser
    return CustomUser.objects.create_user(
        username='admin_view_test',
        password='TestPass123!',
        role='administrateur',
    )


@pytest.fixture
def patient(db):
    from apps.patients.models import Patient
    return Patient.objects.create(
        nom='Durand',
        prenom='Pierre',
        date_naissance=date(1970, 1, 1),
        sexe='M',
        telephone='0699887766',
    )


# ============================================================
# Tests: redirection si non authentifié
# ============================================================

@pytest.mark.django_db
def test_dashboard_requires_login(client):
    """Le tableau de bord doit rediriger vers la page de login."""
    response = client.get('/dashboard/')
    assert response.status_code in (302, 301)
    assert '/accounts/login' in response['Location'] or 'login' in response['Location']


@pytest.mark.django_db
def test_patients_list_requires_login(client):
    """La liste des patients doit rediriger si non connecté."""
    response = client.get('/patients/')
    assert response.status_code in (302, 301)
    assert 'login' in response['Location']


@pytest.mark.django_db
def test_agenda_requires_login(client):
    """L'agenda doit rediriger si non connecté."""
    response = client.get('/agenda/')
    assert response.status_code in (302, 301)
    assert 'login' in response['Location']


@pytest.mark.django_db
def test_consultations_requires_login(client):
    """La liste des consultations doit rediriger si non connecté."""
    response = client.get('/consultations/')
    assert response.status_code in (302, 301)
    assert 'login' in response['Location']


# ============================================================
# Tests: accès avec authentification
# ============================================================

@pytest.mark.django_db
def test_medecin_can_access_dashboard(client, medecin):
    """Un médecin connecté peut accéder au tableau de bord."""
    client.login(username='dr_view_test', password='TestPass123!')
    response = client.get('/dashboard/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_secretaire_can_access_patients_list(client, secretaire):
    """Une secrétaire connectée peut accéder à la liste des patients."""
    client.login(username='sec_view_test', password='TestPass123!')
    response = client.get('/patients/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_medecin_can_access_patients_list(client, medecin):
    """Un médecin connecté peut accéder à la liste des patients."""
    client.login(username='dr_view_test', password='TestPass123!')
    response = client.get('/patients/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_secretaire_can_access_agenda(client, secretaire):
    """Une secrétaire peut accéder à l'agenda."""
    client.login(username='sec_view_test', password='TestPass123!')
    response = client.get('/agenda/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_patient_detail_accessible_by_medecin(client, medecin, patient):
    """Un médecin peut accéder au détail d'un patient."""
    client.login(username='dr_view_test', password='TestPass123!')
    response = client.get(f'/patients/{patient.pk}/')
    assert response.status_code == 200


# ============================================================
# Tests: RBAC - accès interdit
# ============================================================

@pytest.mark.django_db
def test_csv_export_forbidden_for_medecin(client, medecin):
    """Un médecin ne peut pas exporter le CSV des patients (RBAC)."""
    client.login(username='dr_view_test', password='TestPass123!')
    response = client.get('/patients/export/csv/')
    # Doit être 302 (redirect vers accès refusé) ou 403
    assert response.status_code in (302, 403)


@pytest.mark.django_db
def test_csv_export_allowed_for_secretaire(client, secretaire):
    """Une secrétaire peut exporter le CSV des patients."""
    client.login(username='sec_view_test', password='TestPass123!')
    response = client.get('/patients/export/csv/')
    assert response.status_code == 200
    assert 'text/csv' in response['Content-Type']


@pytest.mark.django_db
def test_csv_export_allowed_for_administrateur(client, administrateur):
    """Un administrateur peut exporter le CSV des patients."""
    client.login(username='admin_view_test', password='TestPass123!')
    response = client.get('/patients/export/csv/')
    assert response.status_code == 200
    assert 'text/csv' in response['Content-Type']


# ============================================================
# Tests: API agenda events
# ============================================================

@pytest.mark.django_db
def test_api_events_requires_login(client):
    """L'API events doit refuser les requêtes non authentifiées."""
    response = client.get('/agenda/api/events/')
    assert response.status_code in (302, 401, 403)


@pytest.mark.django_db
def test_api_events_returns_json(client, medecin):
    """L'API events doit retourner du JSON pour un utilisateur connecté."""
    client.login(username='dr_view_test', password='TestPass123!')
    response = client.get('/agenda/api/events/')
    assert response.status_code == 200
    assert response['Content-Type'].startswith('application/json')
