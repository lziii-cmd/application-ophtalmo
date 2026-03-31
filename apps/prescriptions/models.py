"""
Modèles pour les prescriptions médicales.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Prescription(models.Model):
    """
    Prescription médicale: 4 types (R8).
    """

    TYPE_CHOICES = [
        ('lunettes', 'Ordonnance lunettes'),
        ('traitement', 'Traitement médical'),
        ('examen', 'Examen complémentaire'),
        ('lentilles', 'Lentilles de contact'),
    ]

    consultation = models.ForeignKey(
        'consultations.Consultation',
        on_delete=models.PROTECT,
        related_name='prescriptions',
        verbose_name='Consultation'
    )
    medecin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='prescriptions',
        verbose_name='Médecin prescripteur'
    )
    type_prescription = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='Type de prescription'
    )
    contenu = models.JSONField(
        default=dict,
        verbose_name='Contenu de la prescription',
        help_text='Données spécifiques au type de prescription'
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    imprimee = models.BooleanField(default=False, verbose_name='Imprimée')

    class Meta:
        verbose_name = 'Prescription'
        verbose_name_plural = 'Prescriptions'
        ordering = ['-date_creation']

    def __str__(self):
        return f"Prescription {self.get_type_prescription_display()} - {self.consultation.patient.nom_complet} - {self.date_creation.strftime('%d/%m/%Y')}"

    @property
    def patient(self):
        return self.consultation.patient


# Structures de contenu par type de prescription:
# lunettes: {
#   oeil_droit: {sphere, cylindre, axe, addition},
#   oeil_gauche: {sphere, cylindre, axe, addition},
#   remarques: str
# }
# traitement: {
#   medicaments: [{nom, posologie, duree, instructions}],
#   remarques: str
# }
# examen: {
#   examens: [{nom, indication, urgence}],
#   remarques: str
# }
# lentilles: {
#   oeil_droit: {rayon, diametre, puissance, marque},
#   oeil_gauche: {rayon, diametre, puissance, marque},
#   renouvellement: str,
#   remarques: str
# }
