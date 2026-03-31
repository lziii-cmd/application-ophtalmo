"""
URLs pour l'application audit.
"""

from django.urls import path
from . import views

app_name = 'audit'

urlpatterns = [
    path('', views.audit_list_view, name='list'),
]
