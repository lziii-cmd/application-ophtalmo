"""
URLs pour le tableau de bord.
"""

from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index_view, name='index'),
]
