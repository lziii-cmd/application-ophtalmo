"""
Décorateurs RBAC pour la gestion des accès par rôle.
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def role_required(*roles):
    """
    Décorateur qui vérifie que l'utilisateur est connecté et possède
    l'un des rôles spécifiés.

    Usage:
        @role_required('medecin', 'administrateur')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')

            # Les superusers ont toujours accès
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)

            if request.user.role not in roles:
                messages.error(
                    request,
                    "Vous n'avez pas les autorisations nécessaires pour accéder à cette page."
                )
                return HttpResponseForbidden(
                    "<h1>403 - Accès refusé</h1>"
                    "<p>Vous n'avez pas les autorisations pour accéder à cette ressource.</p>"
                    "<a href='/dashboard/'>Retour au tableau de bord</a>"
                )
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


def medecin_required(view_func):
    """Raccourci: accès réservé au médecin."""
    return role_required('medecin', 'administrateur')(view_func)


def secretaire_required(view_func):
    """Raccourci: accès réservé à la secrétaire."""
    return role_required('secretaire', 'administrateur')(view_func)


def admin_required(view_func):
    """Raccourci: accès réservé à l'administrateur."""
    return role_required('administrateur')(view_func)


def staff_required(view_func):
    """Raccourci: accès pour tout le personnel."""
    return role_required('medecin', 'secretaire', 'administrateur')(view_func)
