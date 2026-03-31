"""
Modèles pour le module chirurgie ophtalmologique.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Intervention(models.Model):
    TYPE_CHOICES = [
        ('cataracte', 'Cataracte'),
        ('glaucome', 'Glaucome'),
        ('decollement_retine', 'Décollement de rétine'),
        ('lasik', 'LASIK / Réfractif'),
        ('strabisme', 'Strabisme'),
        ('pterygion', 'Ptérygion'),
        ('greffe_cornee', 'Greffe de cornée'),
        ('autre', 'Autre'),
    ]
    OEIL_CHOICES = [
        ('od', 'Œil droit (OD)'),
        ('og', 'Œil gauche (OG)'),
        ('les_deux', 'Les deux yeux'),
    ]
    STATUT_CHOICES = [
        ('planifiee', 'Planifiée'),
        ('pre_op_valide', 'Bilan pré-op validé'),
        ('realisee', 'Réalisée'),
        ('reportee', 'Reportée'),
        ('annulee', 'Annulée'),
    ]
    ANESTHESIE_CHOICES = [
        ('locale', 'Locale'),
        ('generale', 'Générale'),
        ('sedation', 'Sédation'),
    ]

    # Relations
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.PROTECT,
        related_name='interventions'
    )
    chirurgien = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='interventions_chirurgien',
        limit_choices_to={'role': 'medecin'}
    )
    consultation_origine = models.ForeignKey(
        'consultations.Consultation',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='interventions'
    )
    rdv_operation = models.OneToOneField(
        'agenda.RendezVous',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='intervention'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='interventions_creees'
    )

    # Informations de base
    type_intervention = models.CharField(max_length=30, choices=TYPE_CHOICES)
    type_autre = models.CharField(max_length=100, blank=True, verbose_name="Préciser si autre")
    oeil = models.CharField(max_length=10, choices=OEIL_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='planifiee')
    date_planifiee = models.DateTimeField(verbose_name="Date planifiée")

    # Pré-opératoire
    anesthesie = models.CharField(
        max_length=20, choices=ANESTHESIE_CHOICES, blank=True,
        verbose_name="Type d'anesthésie"
    )
    consentement_signe = models.BooleanField(default=False, verbose_name="Consentement signé")
    bilan_pre_op = models.TextField(blank=True, verbose_name="Bilan pré-opératoire")
    date_rdv_pre_op = models.DateField(null=True, blank=True, verbose_name="Date RDV pré-op")

    # Opération
    date_realisation = models.DateTimeField(null=True, blank=True, verbose_name="Date de réalisation")
    duree_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name="Durée (minutes)")
    compte_rendu = models.TextField(blank=True, verbose_name="Compte-rendu opératoire")
    complications = models.TextField(blank=True, verbose_name="Complications")

    # Post-opératoire
    acuite_post_op_od = models.CharField(max_length=10, blank=True, verbose_name="Acuité post-op OD")
    acuite_post_op_og = models.CharField(max_length=10, blank=True, verbose_name="Acuité post-op OG")
    notes_post_op = models.TextField(blank=True, verbose_name="Notes post-opératoires")

    # Méta
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_planifiee']
        verbose_name = 'Intervention'
        verbose_name_plural = 'Interventions'

    def __str__(self):
        return f"{self.get_type_intervention_display()} — {self.patient} ({self.date_planifiee.strftime('%d/%m/%Y')})"

    @property
    def type_label(self):
        if self.type_intervention == 'autre' and self.type_autre:
            return self.type_autre
        return self.get_type_intervention_display()

    @property
    def statut_couleur(self):
        couleurs = {
            'planifiee': 'warning',
            'pre_op_valide': 'info',
            'realisee': 'success',
            'reportee': 'secondary',
            'annulee': 'danger',
        }
        return couleurs.get(self.statut, 'secondary')

    @property
    def nb_suivis_realises(self):
        return self.suivis.filter(realise=True).count()

    @property
    def nb_suivis_total(self):
        return self.suivis.count()


class SuiviPostOp(models.Model):
    TYPE_CHOICES = [
        ('j1', 'J+1'),
        ('j7', 'J+7'),
        ('j30', 'J+30'),
        ('j90', 'J+90'),
        ('autre', 'Autre'),
    ]

    intervention = models.ForeignKey(
        Intervention,
        on_delete=models.CASCADE,
        related_name='suivis'
    )
    rdv = models.OneToOneField(
        'agenda.RendezVous',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='suivi_post_op'
    )

    type_suivi = models.CharField(max_length=10, choices=TYPE_CHOICES)
    date_prevue = models.DateField(verbose_name="Date prévue")
    date_realisation = models.DateField(null=True, blank=True, verbose_name="Date de réalisation")
    realise = models.BooleanField(default=False)

    acuite_od = models.CharField(max_length=10, blank=True, verbose_name="Acuité OD")
    acuite_og = models.CharField(max_length=10, blank=True, verbose_name="Acuité OG")
    tension_od = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Tension OD")
    tension_og = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True, verbose_name="Tension OG")
    notes = models.TextField(blank=True, verbose_name="Notes")

    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )

    class Meta:
        ordering = ['date_prevue']
        verbose_name = 'Suivi post-opératoire'
        verbose_name_plural = 'Suivis post-opératoires'

    def __str__(self):
        return f"{self.get_type_suivi_display()} — {self.intervention}"
