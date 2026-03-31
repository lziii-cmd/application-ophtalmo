"""
Validateurs de mot de passe pour la clinique ophtalmologique.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MedicalPasswordValidator:
    """
    Valide que le mot de passe contient au moins:
    - 8 caractères
    - 1 lettre majuscule
    - 1 chiffre
    - 1 caractère spécial
    """

    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(
                _("Le mot de passe doit contenir au moins 8 caractères."),
                code='password_too_short',
            )
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins une lettre majuscule."),
                code='password_no_upper',
            )
        if not re.search(r'\d', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un chiffre."),
                code='password_no_digit',
            )
        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=\[\]\\;\'`~/]', password):
            raise ValidationError(
                _("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&* etc.)."),
                code='password_no_special',
            )

    def get_help_text(self):
        return _(
            "Votre mot de passe doit contenir au moins 8 caractères, "
            "une lettre majuscule, un chiffre et un caractère spécial."
        )
