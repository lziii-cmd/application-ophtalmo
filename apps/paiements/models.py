"""
Modèles pour la gestion des paiements.
Règles R9, R10, R11, R12
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal


class Paiement(models.Model):
    """
    Enregistrement de paiement (suivi uniquement, pas caisse).
    Règles: R9, R10, R11, R12
    """

    TYPE_PAIEMENT_CHOICES = [
        ('consultation', 'Consultation'),
        ('lunettes', 'Lunettes'),
        ('traitement', 'Traitement'),
        ('autre', 'Autre'),
    ]

    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('cheque', 'Chèque'),
        ('carte', 'Carte bancaire'),
        ('virement', 'Virement'),
        ('autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('paye', 'Payé'),
        ('partiel', 'Partiel'),
        ('non_paye', 'Non payé'),
    ]

    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.PROTECT,
        related_name='paiements',
        verbose_name='Patient'
    )
    consultation = models.ForeignKey(
        'consultations.Consultation',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='paiements',
        verbose_name='Consultation associée'
    )
    montant = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Montant (€)'
    )
    montant_total_du = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name='Montant total dû (€)',
        help_text='Montant total de la consultation/acte'
    )
    date = models.DateField(default=timezone.now, verbose_name='Date du paiement')
    type_paiement = models.CharField(
        max_length=20,
        choices=TYPE_PAIEMENT_CHOICES,
        default='consultation',
        verbose_name='Type de paiement'
    )
    mode_paiement = models.CharField(
        max_length=20,
        choices=MODE_PAIEMENT_CHOICES,
        default='especes',
        verbose_name='Mode de paiement'
    )
    reference_externe = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Référence externe',
        help_text='N° de chèque, référence virement, etc.'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes'
    )
    valide = models.BooleanField(
        default=False,
        verbose_name='Validé',
        help_text='Seul l\'admin peut modifier un paiement validé (R12)'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='paiements_crees',
        verbose_name='Créé par'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date', '-date_creation']

    def __str__(self):
        return f"Paiement {self.montant}€ - {self.patient.nom_complet} - {self.date.strftime('%d/%m/%Y')}"

    @property
    def statut_calcule(self):
        """
        Calcul automatique du statut de paiement (R11).
        """
        if self.montant_total_du <= 0:
            return 'paye'

        total_paye = self._total_paye_pour_consultation()

        if total_paye >= self.montant_total_du:
            return 'paye'
        elif total_paye > 0:
            return 'partiel'
        else:
            return 'non_paye'

    def _total_paye_pour_consultation(self):
        """Calcule le total payé pour la même consultation."""
        if self.consultation_id:
            from django.db.models import Sum
            total = Paiement.objects.filter(
                consultation_id=self.consultation_id
            ).aggregate(total=Sum('montant'))['total']
            return total or Decimal('0.00')
        return self.montant

    @property
    def reste_a_payer(self):
        """Calcule le reste à payer."""
        if self.montant_total_du <= 0:
            return Decimal('0.00')
        total_paye = self._total_paye_pour_consultation()
        reste = self.montant_total_du - total_paye
        return max(Decimal('0.00'), reste)

    @property
    def est_impaye_depuis_30_jours(self):
        """Alerte si consultation impayée depuis 30 jours."""
        if self.statut_calcule != 'non_paye':
            return False
        delta = timezone.now().date() - self.date
        return delta.days > 30
