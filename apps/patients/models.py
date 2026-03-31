"""
Modèles pour la gestion des patients.
"""

from django.db import models
from django.utils import timezone


class Patient(models.Model):
    """
    Modèle patient avec archivage logique et rétention 10 ans.
    Règles métier: R1, R2, R3
    """

    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
        ('NP', 'Non précisé'),
    ]

    STATUT_CHOICES = [
        ('actif', 'Actif'),
        ('archive', 'Archivé'),
    ]

    nom = models.CharField(max_length=100, verbose_name='Nom')
    prenom = models.CharField(max_length=100, verbose_name='Prénom')
    date_naissance = models.DateField(verbose_name='Date de naissance')
    sexe = models.CharField(
        max_length=2,
        choices=SEXE_CHOICES,
        default='NP',
        verbose_name='Sexe'
    )
    telephone = models.CharField(max_length=20, verbose_name='Téléphone')
    adresse = models.TextField(blank=True, verbose_name='Adresse')
    email = models.EmailField(blank=True, null=True, verbose_name='Email')
    antecedents = models.TextField(
        blank=True,
        verbose_name='Antécédents médicaux',
        help_text='Antécédents médicaux personnels et familiaux'
    )
    allergies = models.TextField(
        blank=True,
        verbose_name='Allergies',
        help_text='Allergies connues (médicaments, autres)'
    )
    traitements_en_cours = models.TextField(
        blank=True,
        verbose_name='Traitements en cours'
    )
    statut = models.CharField(
        max_length=10,
        choices=STATUT_CHOICES,
        default='actif',
        verbose_name='Statut'
    )
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name='Date de création')
    date_modification = models.DateTimeField(auto_now=True, verbose_name='Date de modification')

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'
        ordering = ['nom', 'prenom']

    def __str__(self):
        return f"{self.nom.upper()} {self.prenom} (né(e) le {self.date_naissance.strftime('%d/%m/%Y')})"

    @property
    def age(self):
        """Calcule l'âge du patient."""
        today = timezone.now().date()
        born = self.date_naissance
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    @property
    def nom_complet(self):
        return f"{self.nom.upper()} {self.prenom}"

    @property
    def has_allergies(self):
        """Vérifie si le patient a des allergies renseignées."""
        return bool(self.allergies.strip())

    @property
    def derniere_consultation(self):
        """Retourne la dernière consultation du patient."""
        return self.consultations.filter(
            statut__in=['valide', 'brouillon']
        ).order_by('-date_heure').first()

    @property
    def jours_depuis_derniere_consultation(self):
        """Nombre de jours depuis la dernière consultation."""
        last = self.derniere_consultation
        if last:
            delta = timezone.now() - last.date_heure
            return delta.days
        return None

    @property
    def a_recontacter(self):
        """Patient à recontacter si pas de consultation depuis 12 mois."""
        jours = self.jours_depuis_derniere_consultation
        if jours is None:
            return True  # Jamais consulté
        return jours > 365

    def archiver(self):
        """Archive logiquement le patient (pas de suppression physique - R2)."""
        self.statut = 'archive'
        self.save(update_fields=['statut', 'date_modification'])

    def reactiver(self):
        """Réactive un patient archivé."""
        self.statut = 'actif'
        self.save(update_fields=['statut', 'date_modification'])
