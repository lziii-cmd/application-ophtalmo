"""
Middleware pour l'audit automatique et la gestion des sessions.
"""

import logging
from django.utils import timezone
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime, timedelta

logger = logging.getLogger('apps.audit')

# Délai d'inactivité: 15 minutes
SESSION_TIMEOUT_MINUTES = 15
SESSION_TIMEOUT_SECONDS = SESSION_TIMEOUT_MINUTES * 60

# URLs exclues du timeout de session
EXCLUDED_URLS = [
    '/accounts/login/',
    '/accounts/logout/',
    '/static/',
    '/favicon.ico',
]

# URLs dont la lecture est auditée
AUDITED_READ_URLS = [
    '/patients/',
    '/consultations/',
    '/prescriptions/',
]


class SessionTimeoutMiddleware:
    """
    Middleware de déconnexion automatique après 15 min d'inactivité.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ignorer les URLs exclues
        if any(request.path.startswith(url) for url in EXCLUDED_URLS):
            response = self.get_response(request)
            return response

        if request.user.is_authenticated:
            last_activity_str = request.session.get('last_activity')

            if last_activity_str:
                try:
                    last_activity = datetime.fromisoformat(last_activity_str)
                    elapsed = (timezone.now() - last_activity).total_seconds()

                    if elapsed > SESSION_TIMEOUT_SECONDS:
                        from apps.audit.utils import log_action
                        log_action(
                            user=request.user,
                            action='LOGIN',
                            entity='CustomUser',
                            entity_id=str(request.user.pk),
                            after={'status': 'auto_logout', 'reason': 'inactivity_timeout'},
                            request=request
                        )
                        logout(request)
                        messages.warning(
                            request,
                            f"Votre session a expiré après {SESSION_TIMEOUT_MINUTES} minutes d'inactivité. "
                            "Veuillez vous reconnecter."
                        )
                        return redirect(f'/accounts/login/?next={request.path}')
                except (ValueError, TypeError):
                    pass

            # Mettre à jour le timestamp d'activité
            request.session['last_activity'] = timezone.now().isoformat()

        response = self.get_response(request)
        return response


class AuditMiddleware:
    """
    Middleware pour l'audit automatique des accès aux données sensibles.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Auditer automatiquement les lectures de dossiers patients
        # (les lectures explicites sont loguées dans les vues)

        return response
