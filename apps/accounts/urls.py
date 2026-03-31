"""
URLs pour l'application accounts.
"""

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('utilisateurs/', views.users_list_view, name='users_list'),
    path('utilisateurs/creer/', views.user_create_view, name='user_create'),
    path('utilisateurs/<int:pk>/modifier/', views.user_edit_view, name='user_edit'),
    path('utilisateurs/<int:pk>/deverrouiller/', views.user_unlock_view, name='user_unlock'),
    path('utilisateurs/<int:pk>/toggle-actif/', views.user_toggle_active_view, name='user_toggle_active'),
]
