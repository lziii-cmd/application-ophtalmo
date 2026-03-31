"""
URLs pour l'API REST.
"""

from django.urls import path
from . import views

urlpatterns = [
    path('patients/', views.PatientListAPIView.as_view(), name='api_patients_list'),
    path('patients/<int:pk>/', views.PatientDetailAPIView.as_view(), name='api_patients_detail'),
    path('consultations/', views.ConsultationListAPIView.as_view(), name='api_consultations_list'),
    path('agenda/events/', views.agenda_events_api, name='api_agenda_events'),
]
