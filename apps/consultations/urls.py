"""
URLs pour l'application consultations.
"""

from django.urls import path
from . import views

app_name = 'consultations'

urlpatterns = [
    path('', views.consultation_list_view, name='list'),
    path('nouvelle/', views.consultation_create_view, name='create'),
    path('<int:pk>/', views.consultation_detail_view, name='detail'),
    path('<int:pk>/modifier/', views.consultation_edit_view, name='edit'),
    path('<int:pk>/valider/', views.consultation_validate_view, name='validate'),
    path('<int:pk>/annuler/', views.consultation_cancel_view, name='cancel'),
    path('api/historique/<int:patient_id>/', views.consultation_history_api, name='history_api'),
]
