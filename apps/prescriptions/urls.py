"""
URLs pour l'application prescriptions.
"""

from django.urls import path
from . import views

app_name = 'prescriptions'

urlpatterns = [
    path('', views.prescription_list_view, name='list'),
    path('nouvelle/<int:consultation_pk>/', views.prescription_create_view, name='create'),
    path('<int:pk>/', views.prescription_detail_view, name='detail'),
    path('<int:pk>/pdf/', views.prescription_pdf_view, name='pdf'),
]
