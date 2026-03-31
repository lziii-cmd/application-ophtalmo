from django.urls import path
from . import views

app_name = 'chirurgie'

urlpatterns = [
    path('', views.intervention_list_view, name='list'),
    path('nouvelle/', views.intervention_create_view, name='create'),
    path('<int:pk>/', views.intervention_detail_view, name='detail'),
    path('<int:pk>/modifier/', views.intervention_edit_view, name='edit'),
    path('<int:pk>/compte-rendu/', views.compte_rendu_view, name='compte_rendu'),
    path('<int:pk>/suivi/', views.suivi_create_view, name='suivi_create'),
    path('<int:pk>/valider-pre-op/', views.intervention_valider_pre_op, name='valider_pre_op'),
    path('<int:pk>/annuler/', views.intervention_annuler, name='annuler'),
]
