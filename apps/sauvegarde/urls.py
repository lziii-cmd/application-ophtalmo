"""
URLs pour l'application sauvegarde.
"""

from django.urls import path
from . import views

app_name = 'sauvegarde'

urlpatterns = [
    path('', views.sauvegarde_dashboard_view, name='dashboard'),
    path('creer/', views.sauvegarde_create_view, name='create'),
    path('<int:pk>/restaurer/', views.sauvegarde_restore_confirm_view, name='restore_confirm'),
    path('<int:pk>/restaurer/confirmer/', views.sauvegarde_restore_view, name='restore'),
    path('<int:pk>/telecharger/', views.sauvegarde_download_view, name='download'),
]
