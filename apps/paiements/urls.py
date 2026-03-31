"""
URLs pour l'application paiements.
"""

from django.urls import path
from . import views

app_name = 'paiements'

urlpatterns = [
    path('', views.paiement_list_view, name='list'),
    path('nouveau/', views.paiement_create_view, name='create'),
    path('<int:pk>/modifier/', views.paiement_edit_view, name='edit'),
    path('<int:pk>/valider/', views.paiement_validate_view, name='validate'),
    path('patient/<int:patient_pk>/', views.paiement_patient_view, name='patient_paiements'),
    path('api/consultations/', views.get_consultations_for_patient, name='api_consultations'),
]
