"""
Utilitaires pour la journalisation d'audit.
"""

import logging
from django.utils import timezone

logger = logging.getLogger('apps.audit')


def get_client_ip(request):
    """Extrait l'adresse IP du client."""
    if request is None:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def log_action(user, action, entity, entity_id, before=None, after=None, request=None):
    """
    Enregistre une action dans le journal d'audit.

    Args:
        user: L'utilisateur effectuant l'action (peut être None)
        action: Type d'action (CREATE, UPDATE, DELETE, READ, LOGIN, BACKUP, RESTORE)
        entity: Nom de l'entité concernée (ex: 'Patient', 'Consultation')
        entity_id: Identifiant de l'entité (converti en string)
        before: Données avant modification (dict, optionnel)
        after: Données après modification (dict, optionnel)
        request: Requête HTTP (pour extraire IP et User-Agent)
    """
    from .models import AuditLog

    try:
        ip_address = get_client_ip(request)
        user_agent = ''
        if request:
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]

        AuditLog.objects.create(
            horodatage=timezone.now(),
            utilisateur=user if (user and hasattr(user, 'pk') and user.pk) else None,
            action=action,
            entite=entity,
            entite_id=str(entity_id) if entity_id else '',
            valeur_avant=before,
            valeur_apres=after,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    except Exception as e:
        # Ne jamais laisser l'audit bloquer l'application
        logger.error(f"Erreur lors de l'enregistrement de l'audit: {e}", exc_info=True)
