"""
Modèles pour la gestion des sauvegardes.
Règles R15, R16, R17, R18
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Sauvegarde(models.Model):
    """
    Enregistrement d'une sauvegarde avec chiffrement AES-256.
    """

    TYPE_CHOICES = [
        ('complete', 'Complète'),
        ('incrementale', 'Incrémentale'),
    ]

    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('reussie', 'Réussie'),
        ('echec', 'Échec'),
    ]

    date_heure = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date et heure'
    )
    type_sauvegarde = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Type de sauvegarde'
    )
    fichier_path = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Chemin du fichier'
    )
    taille_octets = models.BigIntegerField(
        default=0,
        verbose_name='Taille (octets)'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_cours',
        verbose_name='Statut'
    )
    nombre_enregistrements = models.IntegerField(
        default=0,
        verbose_name='Nombre d\'enregistrements'
    )
    message_erreur = models.TextField(
        blank=True,
        verbose_name='Message d\'erreur'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sauvegardes',
        verbose_name='Créé par'
    )

    class Meta:
        verbose_name = 'Sauvegarde'
        verbose_name_plural = 'Sauvegardes'
        ordering = ['-date_heure']

    def __str__(self):
        return f"Sauvegarde {self.get_type_sauvegarde_display()} - {self.date_heure.strftime('%d/%m/%Y %H:%M')} - {self.get_statut_display()}"

    @property
    def taille_lisible(self):
        """Retourne la taille en format lisible."""
        taille = self.taille_octets
        if taille < 1024:
            return f"{taille} o"
        elif taille < 1024 * 1024:
            return f"{taille / 1024:.1f} Ko"
        elif taille < 1024 * 1024 * 1024:
            return f"{taille / (1024 * 1024):.1f} Mo"
        else:
            return f"{taille / (1024 * 1024 * 1024):.1f} Go"
