"""
URLs pour l'application patients.
"""

from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list_view, name='list'),
    path('nouveau/', views.patient_create_view, name='create'),
    path('<int:pk>/', views.patient_detail_view, name='detail'),
    path('<int:pk>/modifier/', views.patient_edit_view, name='edit'),
    path('<int:pk>/archiver/', views.patient_archive_view, name='archive'),
    path('<int:pk>/reactiver/', views.patient_reactivate_view, name='reactivate'),
    path('<int:pk>/export-pdf/', views.patient_export_pdf_view, name='export_pdf'),
    path('api/recherche/', views.patient_search_api, name='search_api'),
]
