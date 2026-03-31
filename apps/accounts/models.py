"""
Modèles pour la gestion des comptes utilisateurs.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class CustomUser(AbstractUser):
    """Utilisateur personnalisé avec rôles et gestion de sécurité."""

    ROLE_CHOICES = [
        ('medecin', 'Médecin'),
        ('secretaire', 'Secrétaire'),
        ('administrateur', 'Administrateur'),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='secretaire',
        verbose_name='Rôle'
    )
    failed_login_count = models.IntegerField(
        default=0,
        verbose_name='Tentatives de connexion échouées'
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Compte verrouillé jusqu\'au'
    )
    rpps = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name='Numéro RPPS'
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Téléphone'
    )
    specialite = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Spécialité'
    )

    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        full_name = self.get_full_name()
        if full_name:
            return f"{full_name} ({self.get_role_display()})"
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_locked(self):
        """Vérifie si le compte est verrouillé."""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    @property
    def is_medecin(self):
        return self.role == 'medecin'

    @property
    def is_secretaire(self):
        return self.role == 'secretaire'

    @property
    def is_administrateur(self):
        return self.role == 'administrateur'

    def increment_failed_login(self):
        """Incrémente le compteur d'échecs de connexion."""
        self.failed_login_count += 1
        if self.failed_login_count >= 5:
            self.locked_until = timezone.now() + timezone.timedelta(minutes=30)
        self.save(update_fields=['failed_login_count', 'locked_until'])

    def reset_failed_login(self):
        """Réinitialise le compteur d'échecs de connexion."""
        self.failed_login_count = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_count', 'locked_until'])

    def unlock_account(self):
        """Déverrouille le compte (admin seulement)."""
        self.failed_login_count = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_count', 'locked_until'])
