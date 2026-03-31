"""
URLs pour l'application agenda.
"""

from django.urls import path
from . import views

app_name = 'agenda'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('nouveau/', views.rdv_create_view, name='rdv_create'),
    path('<int:pk>/', views.rdv_detail_view, name='rdv_detail'),
    path('<int:pk>/modifier/', views.rdv_edit_view, name='rdv_edit'),
    path('<int:pk>/annuler/', views.rdv_cancel_view, name='rdv_cancel'),
    path('api/evenements/', views.rdv_api_events, name='api_events'),
    path('api/events/', views.calendar_events_api, name='events_api'),
    path('api/events/<int:pk>/move/', views.rdv_move_api, name='rdv_move'),
]
