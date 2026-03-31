"""
Modèles pour la gestion de l'agenda et des rendez-vous.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class RendezVous(models.Model):
    """
    Rendez-vous avec vérification des conflits (R4).
    """

    STATUT_CHOICES = [
        ('programme', 'Programmé'),
        ('effectue', 'Effectué'),
        ('annule', 'Annulé'),
        ('non_presente', 'Non présenté'),
    ]

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.PROTECT,
        related_name='rendez_vous',
        verbose_name='Patient'
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='rendez_vous_medecin',
        limit_choices_to={'role': 'medecin'},
        verbose_name='Médecin'
    )
    date_heure = models.DateTimeField(verbose_name='Date et heure')
    duree = models.IntegerField(
        default=20,
        verbose_name='Durée (minutes)',
        help_text='Durée du rendez-vous en minutes'
    )
    motif = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Motif du rendez-vous'
    )
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='programme',
        verbose_name='Statut'
    )
    motif_annulation = models.TextField(
        blank=True,
        verbose_name='Motif d\'annulation',
        help_text='Obligatoire si le rendez-vous est annulé'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='rdv_crees',
        verbose_name='Créé par'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Rendez-vous'
        verbose_name_plural = 'Rendez-vous'
        ordering = ['-date_heure']

    def __str__(self):
        return f"RDV {self.patient.nom_complet} - {self.date_heure.strftime('%d/%m/%Y %H:%M')}"

    @property
    def heure_fin(self):
        """Calcule l'heure de fin du rendez-vous."""
        return self.date_heure + timedelta(minutes=self.duree)

    def check_conflict(self, exclude_self=False):
        """
        Vérifie les conflits de rendez-vous pour le médecin (R4).
        Retourne True si conflit, False sinon.
        """
        debut = self.date_heure
        fin = self.heure_fin

        qs = RendezVous.objects.filter(
            medecin=self.medecin,
            statut__in=['programme', 'effectue'],
            date_heure__lt=fin,
        ).exclude(
            date_heure__gte=fin
        )

        # Exclure les rendez-vous qui finissent avant le début
        qs = qs.filter(
            date_heure__lt=fin
        )

        if exclude_self and self.pk:
            qs = qs.exclude(pk=self.pk)

        # Vérification manuelle pour les fins de RDV
        for rdv in qs:
            rdv_fin = rdv.date_heure + timedelta(minutes=rdv.duree)
            if rdv.date_heure < fin and rdv_fin > debut:
                return True
        return False

    def save(self, *args, **kwargs):
        """Validation du motif d'annulation si statut = annule."""
        if self.statut == 'annule' and not self.motif_annulation:
            raise ValueError("Le motif d'annulation est obligatoire.")
        super().save(*args, **kwargs)
