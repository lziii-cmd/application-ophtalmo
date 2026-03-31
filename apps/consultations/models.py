"""
Modèles pour les consultations médicales.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Consultation(models.Model):
    """
    Consultation médicale ophtalmologique.
    Règles R1, R5, R6, R7, R8
    """

    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('valide', 'Validée'),
        ('annule', 'Annulée'),
    ]

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.PROTECT,
        related_name='consultations',
        verbose_name='Patient'
    )
    rendez_vous = models.OneToOneField(
        'agenda.RendezVous',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultation',
        verbose_name='Rendez-vous associé'
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='consultations',
        limit_choices_to={'role': 'medecin'},
        verbose_name='Médecin'
    )
    date_heure = models.DateTimeField(
        default=timezone.now,
        verbose_name='Date et heure'
    )

    # Acuité visuelle
    acuite_od_loin = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Acuité OD de loin',
        help_text='Exemple: 10/10, 8/10, 3/10'
    )
    acuite_og_loin = models.CharField(
        max_length=10,
        blank=True,
        verbose_name='Acuité OG de loin'
    )
    acuite_od_pres = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Acuité OD de près'
    )
    acuite_og_pres = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Acuité OG de près'
    )

    # Tension oculaire (mmHg)
    tension_od = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='Tension OD (mmHg)'
    )
    tension_og = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name='Tension OG (mmHg)'
    )

    # Diagnostic
    diagnostic_principal = models.TextField(
        verbose_name='Diagnostic principal'
    )
    code_cim10_principal = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Code CIM-10 principal',
        help_text='Ex: H52.1 pour myopie'
    )
    diagnostics_associes = models.JSONField(
        default=list,
        blank=True,
        verbose_name='Diagnostics associés',
        help_text='Liste de diagnostics secondaires avec codes CIM-10'
    )
    actes_realises = models.TextField(
        blank=True,
        verbose_name='Actes réalisés'
    )
    observations = models.TextField(
        blank=True,
        verbose_name='Observations et notes'
    )

    # Statut
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='brouillon',
        verbose_name='Statut'
    )
    motif_annulation = models.TextField(
        blank=True,
        verbose_name='Motif d\'annulation'
    )
    date_validation = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date de validation'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Consultation'
        verbose_name_plural = 'Consultations'
        ordering = ['-date_heure']

    def __str__(self):
        return f"Consultation {self.patient.nom_complet} - {self.date_heure.strftime('%d/%m/%Y')}"

    @property
    def tension_od_anormale(self):
        """Alerte si tension OD anormale (< 10 ou > 21 mmHg)."""
        if self.tension_od is not None:
            return float(self.tension_od) < 10 or float(self.tension_od) > 21
        return False

    @property
    def tension_og_anormale(self):
        """Alerte si tension OG anormale (< 10 ou > 21 mmHg)."""
        if self.tension_og is not None:
            return float(self.tension_og) < 10 or float(self.tension_og) > 21
        return False

    @property
    def alertes_tension(self):
        """Retourne les alertes de tension oculaire."""
        alertes = []
        if self.tension_od_anormale:
            alertes.append(f"Tension OD anormale: {self.tension_od} mmHg")
        if self.tension_og_anormale:
            alertes.append(f"Tension OG anormale: {self.tension_og} mmHg")
        return alertes

    @property
    def peut_etre_modifiee(self):
        """Une consultation validée ne peut plus être modifiée (R7)."""
        return self.statut == 'brouillon'

    def valider(self):
        """Valide la consultation (R7 - après validation, seule l'annulation est possible)."""
        if self.statut != 'brouillon':
            raise ValueError("Seule une consultation en brouillon peut être validée.")
        self.statut = 'valide'
        self.date_validation = timezone.now()
        self.save(update_fields=['statut', 'date_validation', 'date_modification'])

    def annuler(self, motif):
        """Annule la consultation avec un motif obligatoire."""
        if not motif:
            raise ValueError("Le motif d'annulation est obligatoire.")
        self.statut = 'annule'
        self.motif_annulation = motif
        self.save(update_fields=['statut', 'motif_annulation', 'date_modification'])
