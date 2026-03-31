"""
Modèle du journal d'audit immuable.
Règles R13, R14
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class AuditLog(models.Model):
    """
    Journal d'audit immuable - R13, R14.
    Aucun utilisateur ne peut modifier ou supprimer les entrées.
    """

    ACTION_CHOICES = [
        ('CREATE', 'Création'),
        ('UPDATE', 'Modification'),
        ('DELETE', 'Suppression'),
        ('READ', 'Consultation'),
        ('LOGIN', 'Connexion'),
        ('BACKUP', 'Sauvegarde'),
        ('RESTORE', 'Restauration'),
    ]

    horodatage = models.DateTimeField(
        default=timezone.now,
        verbose_name='Horodatage (UTC)',
        db_index=True
    )
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Utilisateur'
    )
    action = models.CharField(
        max_length=20,
        choices=ACTION_CHOICES,
        verbose_name='Action',
        db_index=True
    )
    entite = models.CharField(
        max_length=100,
        verbose_name='Entité concernée',
        db_index=True
    )
    entite_id = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Identifiant de l\'entité'
    )
    valeur_avant = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Valeur avant modification'
    )
    valeur_apres = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Valeur après modification'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Adresse IP'
    )
    user_agent = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='User Agent'
    )

    class Meta:
        verbose_name = 'Log d\'audit'
        verbose_name_plural = 'Logs d\'audit'
        ordering = ['-horodatage']
        # Aucun droit de modification (appliqué au niveau des vues et de l'admin)

    def __str__(self):
        user_str = str(self.utilisateur) if self.utilisateur else 'Anonyme'
        return f"[{self.horodatage.strftime('%d/%m/%Y %H:%M')}] {self.action} {self.entite} par {user_str}"

    def save(self, *args, **kwargs):
        """
        Empêche la modification d'une entrée existante (R14).
        Les entrées d'audit sont immuables.
        """
        if self.pk:
            raise PermissionError(
                "Les entrées du journal d'audit sont immuables et ne peuvent pas être modifiées."
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Empêche la suppression d'entrées d'audit (R14)."""
        raise PermissionError(
            "Les entrées du journal d'audit sont immuables et ne peuvent pas être supprimées."
        )
