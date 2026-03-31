"""
Commande Django pour insérer des données de test dans toutes les tables.
Usage: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta, datetime
from decimal import Decimal
import random


class Command(BaseCommand):
    help = "Insère des données de test dans toutes les tables"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Insertion des données de test..."))

        with transaction.atomic():
            self._create_users()
            self._create_patients()
            self._create_rendez_vous()
            self._create_consultations()
            self._create_prescriptions()
            self._create_paiements()
            self._create_sauvegardes()

        self.stdout.write(self.style.SUCCESS("Données de test insérées avec succès !"))
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("=== COMPTES DE TEST ==="))
        self.stdout.write("  admin        / Admin@1234    (Administrateur)")
        self.stdout.write("  dr.hassan    / Medecin@1234  (Médecin)")
        self.stdout.write("  secretaire   / Secret@1234   (Secrétaire)")

    def _create_users(self):
        from apps.accounts.models import CustomUser

        users_data = [
            {
                "username": "admin",
                "password": "Admin@1234",
                "first_name": "Admin",
                "last_name": "Système",
                "email": "admin@cabinet.local",
                "role": "administrateur",
                "is_superuser": True,
                "is_staff": True,
            },
            {
                "username": "dr.hassan",
                "password": "Medecin@1234",
                "first_name": "Hassan",
                "last_name": "Diallo",
                "email": "dr.hassan@cabinet.local",
                "role": "medecin",
                "rpps": "10012345678",
                "specialite": "Ophtalmologie",
            },
            {
                "username": "secretaire",
                "password": "Secret@1234",
                "first_name": "Fatou",
                "last_name": "Mbaye",
                "email": "secretaire@cabinet.local",
                "role": "secretaire",
            },
        ]

        self.users = {}
        for data in users_data:
            password = data.pop("password")
            username = data["username"]
            is_superuser = data.pop("is_superuser", False)
            is_staff = data.pop("is_staff", False)

            user, created = CustomUser.objects.get_or_create(
                username=username, defaults=data
            )
            if created:
                user.set_password(password)
                user.is_superuser = is_superuser
                user.is_staff = is_staff
                user.save()
                self.stdout.write(f"  Créé: {username}")
            else:
                self.stdout.write(f"  Existant: {username}")
            self.users[username] = user

    def _create_patients(self):
        from apps.patients.models import Patient

        patients_data = [
            {
                "nom": "NDIAYE",
                "prenom": "Moussa",
                "date_naissance": date(1978, 3, 15),
                "sexe": "M",
                "telephone": "77 123 45 67",
                "adresse": "12 Rue Cheikh Anta Diop, Dakar",
                "email": "moussa.ndiaye@email.com",
                "antecedents": "Diabète type 2 depuis 2015. Hypertension artérielle.",
                "allergies": "Pénicilline (réaction allergique sévère en 2019)",
                "traitements_en_cours": "Metformine 850mg x2/j, Amlodipine 5mg/j",
                "statut": "actif",
            },
            {
                "nom": "FALL",
                "prenom": "Aminata",
                "date_naissance": date(1990, 7, 22),
                "sexe": "F",
                "telephone": "76 234 56 78",
                "adresse": "8 Avenue Bourguiba, Dakar",
                "email": "aminata.fall@email.com",
                "antecedents": "Myopie forte depuis l'enfance. Port de lunettes depuis 8 ans.",
                "allergies": "",
                "traitements_en_cours": "",
                "statut": "actif",
            },
            {
                "nom": "DIOP",
                "prenom": "Ibrahima",
                "date_naissance": date(1955, 11, 8),
                "sexe": "M",
                "telephone": "70 345 67 89",
                "adresse": "45 Rue de Thiès, Dakar",
                "email": "",
                "antecedents": "Glaucome diagnostiqué en 2018. Cataracte oeil droit.",
                "allergies": "Sulfamides",
                "traitements_en_cours": "Travoprost (collyre) 1 goutte/soir OD+OG",
                "statut": "actif",
            },
            {
                "nom": "SARR",
                "prenom": "Marième",
                "date_naissance": date(2001, 5, 30),
                "sexe": "F",
                "telephone": "78 456 78 90",
                "adresse": "23 Cité Keur Gorgui, Dakar",
                "email": "marieme.sarr@email.com",
                "antecedents": "Astigmatisme depuis 2019.",
                "allergies": "",
                "traitements_en_cours": "",
                "statut": "actif",
            },
            {
                "nom": "BA",
                "prenom": "Ousmane",
                "date_naissance": date(1968, 9, 14),
                "sexe": "M",
                "telephone": "77 567 89 01",
                "adresse": "7 Allée des Baobabs, Thiès",
                "email": "ousmane.ba@email.com",
                "antecedents": "Presbytie. Antécédents familiaux de DMLA.",
                "allergies": "",
                "traitements_en_cours": "Suppléments vitaminiques DMLA",
                "statut": "actif",
            },
            {
                "nom": "GUEYE",
                "prenom": "Ndèye",
                "date_naissance": date(1985, 2, 18),
                "sexe": "F",
                "telephone": "76 678 90 12",
                "adresse": "16 Rue Félix Faure, Dakar",
                "email": "ndeye.gueye@email.com",
                "antecedents": "Conjonctivite allergique récurrente.",
                "allergies": "Pollens, acariens",
                "traitements_en_cours": "",
                "statut": "actif",
            },
            {
                "nom": "DIALLO",
                "prenom": "Mamadou",
                "date_naissance": date(1943, 6, 5),
                "sexe": "M",
                "telephone": "70 789 01 23",
                "adresse": "2 Rue du Port, Saint-Louis",
                "email": "",
                "antecedents": "Cataracte bilatérale opérée en 2020. Rétinopathie diabétique.",
                "allergies": "",
                "traitements_en_cours": "Insuline NPH",
                "statut": "actif",
            },
            {
                "nom": "SECK",
                "prenom": "Rokhaya",
                "date_naissance": date(1972, 12, 25),
                "sexe": "F",
                "telephone": "78 890 12 34",
                "adresse": "34 Avenue Lamine Guèye, Dakar",
                "email": "rokhaya.seck@email.com",
                "antecedents": "Hypermétropie modérée.",
                "allergies": "",
                "traitements_en_cours": "",
                "statut": "actif",
            },
            {
                "nom": "CISSE",
                "prenom": "Abdoulaye",
                "date_naissance": date(1995, 8, 11),
                "sexe": "M",
                "telephone": "77 901 23 45",
                "adresse": "9 Cité Liberté, Dakar",
                "email": "abdoulaye.cisse@email.com",
                "antecedents": "Aucun antécédent notable.",
                "allergies": "",
                "traitements_en_cours": "",
                "statut": "actif",
            },
            {
                "nom": "THIAW",
                "prenom": "Bineta",
                "date_naissance": date(1960, 4, 7),
                "sexe": "F",
                "telephone": "76 012 34 56",
                "adresse": "18 Rue Saint-Michel, Dakar",
                "email": "",
                "antecedents": "Syndrome sec oculaire sévère.",
                "allergies": "Conservateurs dans les collyres",
                "traitements_en_cours": "Larmes artificielles sans conservateur",
                "statut": "archive",
            },
        ]

        self.patients = []
        for data in patients_data:
            p, created = Patient.objects.get_or_create(
                nom=data["nom"], prenom=data["prenom"],
                date_naissance=data["date_naissance"],
                defaults=data
            )
            self.patients.append(p)
            if created:
                self.stdout.write(f"  Patient: {p.nom_complet}")

    def _create_rendez_vous(self):
        from apps.agenda.models import RendezVous

        medecin = self.users["dr.hassan"]
        today = timezone.now().replace(hour=8, minute=0, second=0, microsecond=0)

        secretaire = self.users["secretaire"]

        rdv_data = [
            # RDV passés (effectués)
            {
                "patient": self.patients[0],
                "medecin": medecin,
                "date_heure": today - timedelta(days=60, hours=-9),
                "duree": 20,
                "motif": "Contrôle diabète - fond d'œil",
                "statut": "effectue",
                "created_by": secretaire,
            },
            {
                "patient": self.patients[1],
                "medecin": medecin,
                "date_heure": today - timedelta(days=45, hours=-10),
                "duree": 20,
                "motif": "Renouvellement ordonnance lunettes",
                "statut": "effectue",
            },
            {
                "patient": self.patients[2],
                "medecin": medecin,
                "date_heure": today - timedelta(days=30, hours=-8),
                "duree": 30,
                "motif": "Suivi glaucome - tension oculaire",
                "statut": "effectue",
            },
            {
                "patient": self.patients[3],
                "medecin": medecin,
                "date_heure": today - timedelta(days=20, hours=-9),
                "duree": 20,
                "motif": "Première consultation - vision floue",
                "statut": "effectue",
            },
            {
                "patient": self.patients[4],
                "medecin": medecin,
                "date_heure": today - timedelta(days=15, hours=-11),
                "duree": 20,
                "motif": "Contrôle presbytie",
                "statut": "effectue",
            },
            {
                "patient": self.patients[5],
                "medecin": medecin,
                "date_heure": today - timedelta(days=10, hours=-8, minutes=30),
                "duree": 20,
                "motif": "Conjonctivite allergique",
                "statut": "effectue",
            },
            {
                "patient": self.patients[6],
                "medecin": medecin,
                "date_heure": today - timedelta(days=7, hours=-10),
                "duree": 30,
                "motif": "Suivi rétinopathie diabétique",
                "statut": "effectue",
            },
            # RDV annulé
            {
                "patient": self.patients[7],
                "medecin": medecin,
                "date_heure": today - timedelta(days=5, hours=-9),
                "duree": 20,
                "motif": "Contrôle hypermétropie",
                "statut": "annule",
                "motif_annulation": "Patient empêché, reporté",
            },
            # RDV aujourd'hui
            {
                "patient": self.patients[0],
                "medecin": medecin,
                "date_heure": today.replace(hour=9, minute=0),
                "duree": 20,
                "motif": "Contrôle tension oculaire",
                "statut": "programme",
            },
            {
                "patient": self.patients[1],
                "medecin": medecin,
                "date_heure": today.replace(hour=9, minute=30),
                "duree": 20,
                "motif": "Renouvellement lentilles",
                "statut": "programme",
            },
            {
                "patient": self.patients[3],
                "medecin": medecin,
                "date_heure": today.replace(hour=10, minute=0),
                "duree": 20,
                "motif": "Suivi astigmatisme",
                "statut": "programme",
            },
            # RDV futurs
            {
                "patient": self.patients[4],
                "medecin": medecin,
                "date_heure": today + timedelta(days=2, hours=1),
                "duree": 20,
                "motif": "Bilan visuel annuel",
                "statut": "programme",
            },
            {
                "patient": self.patients[7],
                "medecin": medecin,
                "date_heure": today + timedelta(days=3, hours=2),
                "duree": 20,
                "motif": "Contrôle hypermétropie (reporté)",
                "statut": "programme",
            },
            {
                "patient": self.patients[8],
                "medecin": medecin,
                "date_heure": today + timedelta(days=5, hours=1, minutes=30),
                "duree": 20,
                "motif": "Première consultation",
                "statut": "programme",
            },
        ]

        self.rdvs = []
        for data in rdv_data:
            # Assigner created_by par défaut si absent
            if "created_by" not in data:
                data["created_by"] = secretaire
            existing = RendezVous.objects.filter(
                patient=data["patient"],
                date_heure=data["date_heure"]
            ).first()
            if not existing:
                rdv = RendezVous.objects.create(**data)
                self.rdvs.append(rdv)
            else:
                self.rdvs.append(existing)
        self.stdout.write(f"  {len(self.rdvs)} rendez-vous créés/récupérés")

    def _create_consultations(self):
        from apps.consultations.models import Consultation

        medecin = self.users["dr.hassan"]

        # On prend les RDV effectués
        rdvs_effectues = [r for r in self.rdvs if r.statut == "effectue"]

        consultations_data = [
            {
                "rdv_index": 0,
                "patient": self.patients[0],
                "acuite_od_loin": "7/10",
                "acuite_og_loin": "7/10",
                "acuite_od_pres": "P3",
                "acuite_og_pres": "P3",
                "tension_od": Decimal("22.0"),
                "tension_og": Decimal("21.5"),
                "diagnostic_principal": "Rétinopathie diabétique non proliférante modérée, OD et OG",
                "code_cim10_principal": "H36.0",
                "actes_realises": "Fond d'œil bilatéral\nPhotographie du fond d'œil\nMesure de l'acuité visuelle",
                "observations": "Aggravation légère des lésions depuis le dernier contrôle. Tension légèrement élevée OD. Renforcement du traitement local recommandé.",
                "statut": "valide",
            },
            {
                "rdv_index": 1,
                "patient": self.patients[1],
                "acuite_od_loin": "3/10",
                "acuite_og_loin": "2/10",
                "acuite_od_pres": "P2",
                "acuite_og_pres": "P2",
                "tension_od": Decimal("14.0"),
                "tension_og": Decimal("13.5"),
                "diagnostic_principal": "Myopie forte bilatérale avec astigmatisme",
                "code_cim10_principal": "H52.1",
                "diagnostics_associes": [
                    {"code": "H52.2", "libelle": "Astigmatisme"}
                ],
                "actes_realises": "Réfraction subjective\nKératométrie\nMesure de l'acuité visuelle avec correction",
                "observations": "Myopie stable. Nouvelle ordonnance pour lunettes. Correction OD: -5.75 (-1.25 x 180°), OG: -6.00 (-1.50 x 175°)",
                "statut": "valide",
            },
            {
                "rdv_index": 2,
                "patient": self.patients[2],
                "acuite_od_loin": "5/10",
                "acuite_og_loin": "8/10",
                "tension_od": Decimal("25.0"),
                "tension_og": Decimal("24.0"),
                "diagnostic_principal": "Glaucome chronique à angle ouvert, OD et OG",
                "code_cim10_principal": "H40.1",
                "actes_realises": "Tonométrie\nPachymétrie\nChamp visuel\nFond d'œil",
                "observations": "Tension oculaire ÉLEVÉE malgré le traitement en cours. Modification du traitement nécessaire. Suivi rapproché recommandé toutes les 6 semaines.",
                "statut": "valide",
            },
            {
                "rdv_index": 3,
                "patient": self.patients[3],
                "acuite_od_loin": "8/10",
                "acuite_og_loin": "7/10",
                "tension_od": Decimal("14.0"),
                "tension_og": Decimal("15.0"),
                "diagnostic_principal": "Astigmatisme mixte bilatéral",
                "code_cim10_principal": "H52.2",
                "actes_realises": "Réfraction automatique\nRéfraction subjective\nKératométrie",
                "observations": "Premier examen. Astigmatisme significatif. Prescription de lunettes correctrices. Conseils d'hygiène visuelle donnés.",
                "statut": "valide",
            },
            {
                "rdv_index": 4,
                "patient": self.patients[4],
                "acuite_od_loin": "10/10",
                "acuite_og_loin": "10/10",
                "acuite_od_pres": "P5",
                "acuite_og_pres": "P5",
                "tension_od": Decimal("15.0"),
                "tension_og": Decimal("14.5"),
                "diagnostic_principal": "Presbytie bilatérale",
                "code_cim10_principal": "H52.4",
                "actes_realises": "Mesure de l'acuité visuelle de loin et de près\nRéfraction",
                "observations": "Vision de loin normale. Presbytie confirmée. Prescription de verres progressifs. Bilan DMLA satisfaisant.",
                "statut": "valide",
            },
            {
                "rdv_index": 5,
                "patient": self.patients[5],
                "acuite_od_loin": "10/10",
                "acuite_og_loin": "10/10",
                "tension_od": Decimal("13.0"),
                "tension_og": Decimal("12.5"),
                "diagnostic_principal": "Conjonctivite allergique chronique",
                "code_cim10_principal": "H10.1",
                "actes_realises": "Examen à la lampe à fente\nTest fluorescéine",
                "observations": "Crise aiguë. Présence de papilles géantes. Prescription de collyres anti-allergiques et corticoïdes en cure courte.",
                "statut": "valide",
            },
            {
                "rdv_index": 6,
                "patient": self.patients[6],
                "acuite_od_loin": "6/10",
                "acuite_og_loin": "8/10",
                "tension_od": Decimal("16.0"),
                "tension_og": Decimal("15.5"),
                "diagnostic_principal": "Rétinopathie diabétique proliférante OD",
                "code_cim10_principal": "H36.0",
                "diagnostics_associes": [
                    {"code": "H25", "libelle": "Pseudophakie post-cataracte OD"},
                ],
                "actes_realises": "Fond d'œil\nAngiographie rétinienne\nOCT maculaire",
                "observations": "Apparition de néovaisseaux OD. Photocoagulation au laser recommandée en urgence relative. Adressé au CHU.",
                "statut": "brouillon",
            },
        ]

        self.consultations = []
        for item in consultations_data:
            rdv_index = item.pop("rdv_index")
            rdv = rdvs_effectues[rdv_index] if rdv_index < len(rdvs_effectues) else None

            # Vérifier si une consultation existe déjà pour ce patient/rdv
            existing = Consultation.objects.filter(patient=item["patient"]).order_by("date_heure").first()
            if rdv and hasattr(rdv, "consultation"):
                existing = rdv.consultation

            if rdv and not Consultation.objects.filter(rendez_vous=rdv).exists():
                statut = item.pop("statut")
                c = Consultation.objects.create(
                    medecin=medecin,
                    rendez_vous=rdv,
                    date_heure=rdv.date_heure,
                    **item
                )
                if statut == "valide":
                    c.statut = "valide"
                    c.date_validation = timezone.now()
                    c.save(update_fields=["statut", "date_validation"])
                self.consultations.append(c)
            elif rdv and Consultation.objects.filter(rendez_vous=rdv).exists():
                self.consultations.append(Consultation.objects.get(rendez_vous=rdv))

        self.stdout.write(f"  {len(self.consultations)} consultations créées/récupérées")

    def _create_prescriptions(self):
        from apps.prescriptions.models import Prescription

        medecin = self.users["dr.hassan"]

        if not self.consultations:
            return

        prescriptions_data = []

        # Prescription lunettes pour patient myope (consultation 1 - Aminata Fall)
        if len(self.consultations) > 1:
            prescriptions_data.append({
                "consultation": self.consultations[1],
                "type_prescription": "lunettes",
                "contenu": {
                    "od": {"sphere": -5.75, "cylindre": -1.25, "axe": 180, "addition": None},
                    "og": {"sphere": -6.00, "cylindre": -1.50, "axe": 175, "addition": None},
                    "distance_pupillaire": 63,
                    "vergence": "VL (vision de loin)",
                    "notes": "Verres antireflets recommandés. Monture légère.",
                },
                "imprimee": True,
            })

        # Prescription traitement pour glaucome (consultation 2 - Ibrahima Diop)
        if len(self.consultations) > 2:
            prescriptions_data.append({
                "consultation": self.consultations[2],
                "type_prescription": "traitement",
                "contenu": {
                    "medicaments": [
                        {
                            "nom": "Bimatoprost 0,01% collyre",
                            "posologie": "1 goutte",
                            "frequence": "1 fois/soir",
                            "duree": "3 mois",
                            "voie": "Instillation oculaire OD + OG",
                        },
                        {
                            "nom": "Dorzolamide/Timolol collyre",
                            "posologie": "1 goutte",
                            "frequence": "2 fois/jour (matin et soir)",
                            "duree": "3 mois",
                            "voie": "Instillation oculaire OD + OG",
                        },
                    ],
                    "notes": "Surveiller la tension toutes les 6 semaines. Signaler tout changement de la vision.",
                },
                "imprimee": True,
            })

        # Prescription lunettes pour astigmatisme (consultation 3 - Marième Sarr)
        if len(self.consultations) > 3:
            prescriptions_data.append({
                "consultation": self.consultations[3],
                "type_prescription": "lunettes",
                "contenu": {
                    "od": {"sphere": -0.50, "cylindre": -1.75, "axe": 90, "addition": None},
                    "og": {"sphere": -0.25, "cylindre": -2.00, "axe": 85, "addition": None},
                    "distance_pupillaire": 60,
                    "vergence": "VL+VP (verres progressifs non recommandés à cet âge)",
                    "notes": "Port permanent conseillé pour activités scolaires.",
                },
                "imprimee": False,
            })

        # Prescription verres progressifs pour presbytie (consultation 4 - Ousmane Ba)
        if len(self.consultations) > 4:
            prescriptions_data.append({
                "consultation": self.consultations[4],
                "type_prescription": "lunettes",
                "contenu": {
                    "od": {"sphere": 0.0, "cylindre": 0.0, "axe": 0, "addition": 2.0},
                    "og": {"sphere": 0.0, "cylindre": 0.0, "axe": 0, "addition": 2.0},
                    "distance_pupillaire": 65,
                    "vergence": "VP (vision de près) / Verres progressifs",
                    "notes": "Verres progressifs avec addition +2.00. Adaptation progressive conseillée.",
                },
                "imprimee": True,
            })

        # Prescription examen complémentaire pour conjonctivite (consultation 5 - Ndèye Gueye)
        if len(self.consultations) > 5:
            prescriptions_data.append({
                "consultation": self.consultations[5],
                "type_prescription": "traitement",
                "contenu": {
                    "medicaments": [
                        {
                            "nom": "Olopatadine 0,1% collyre",
                            "posologie": "1 goutte",
                            "frequence": "2 fois/jour",
                            "duree": "1 mois",
                            "voie": "Instillation oculaire OD + OG",
                        },
                        {
                            "nom": "Dexaméthasone 0,1% collyre",
                            "posologie": "1 goutte",
                            "frequence": "4 fois/jour pendant 7 jours puis 2 fois/jour pendant 7 jours",
                            "duree": "14 jours",
                            "voie": "Instillation oculaire OD + OG",
                        },
                        {
                            "nom": "Larmes artificielles sans conservateur",
                            "posologie": "1-2 gouttes",
                            "frequence": "Selon besoin (jusqu'à 6 fois/jour)",
                            "duree": "Traitement de fond",
                            "voie": "Instillation oculaire",
                        },
                    ],
                    "notes": "Éviter les allergènes connus. Lunettes de soleil en extérieur.",
                },
                "imprimee": True,
            })

        # Prescription examen complémentaire pour rétinopathie (consultation 0 - Moussa Ndiaye)
        if len(self.consultations) > 0:
            prescriptions_data.append({
                "consultation": self.consultations[0],
                "type_prescription": "examen",
                "contenu": {
                    "type_examen": "Angiographie à la fluorescéine + OCT maculaire",
                    "urgence": "Sous 4 semaines",
                    "etablissement": "CHU de Dakar - Service Ophtalmologie",
                    "notes": "Contrôle de la rétinopathie diabétique. Résultats à apporter au prochain RDV.",
                },
                "imprimee": False,
            })

        self.prescriptions = []
        for data in prescriptions_data:
            consult = data["consultation"]
            ptype = data["type_prescription"]
            existing = Prescription.objects.filter(
                consultation=consult, type_prescription=ptype
            ).first()
            if not existing:
                p = Prescription.objects.create(medecin=medecin, **data)
                self.prescriptions.append(p)
            else:
                self.prescriptions.append(existing)

        self.stdout.write(f"  {len(self.prescriptions)} prescriptions créées/récupérées")

    def _create_paiements(self):
        from apps.paiements.models import Paiement

        secretaire = self.users["secretaire"]
        today = timezone.now().date()

        paiements_data = [
            # Paiement complet - Aminata Fall (consultation lunettes)
            {
                "patient": self.patients[1],
                "consultation": self.consultations[1] if len(self.consultations) > 1 else None,
                "montant": Decimal("15000.00"),
                "montant_total_du": Decimal("15000.00"),
                "date": today - timedelta(days=45),
                "type_paiement": "consultation",
                "mode_paiement": "carte",
                "reference_externe": "CB-2025-001247",
                "notes": "Consultation + réfraction",
                "valide": True,
            },
            # Paiement partiel - Ibrahima Diop (glaucome)
            {
                "patient": self.patients[2],
                "consultation": self.consultations[2] if len(self.consultations) > 2 else None,
                "montant": Decimal("10000.00"),
                "montant_total_du": Decimal("20000.00"),
                "date": today - timedelta(days=30),
                "type_paiement": "consultation",
                "mode_paiement": "cheque",
                "reference_externe": "CHQ-00892",
                "notes": "Premier versement - solde à régler",
                "valide": True,
            },
            # Paiement complet - Marième Sarr
            {
                "patient": self.patients[3],
                "consultation": self.consultations[3] if len(self.consultations) > 3 else None,
                "montant": Decimal("12000.00"),
                "montant_total_du": Decimal("12000.00"),
                "date": today - timedelta(days=20),
                "type_paiement": "consultation",
                "mode_paiement": "especes",
                "valide": True,
            },
            # Paiement complet - Ousmane Ba
            {
                "patient": self.patients[4],
                "consultation": self.consultations[4] if len(self.consultations) > 4 else None,
                "montant": Decimal("12000.00"),
                "montant_total_du": Decimal("12000.00"),
                "date": today - timedelta(days=15),
                "type_paiement": "consultation",
                "mode_paiement": "virement",
                "reference_externe": "VIR-2025-0156",
                "valide": False,
            },
            # Paiement lunettes - Aminata Fall
            {
                "patient": self.patients[1],
                "montant": Decimal("85000.00"),
                "montant_total_du": Decimal("85000.00"),
                "date": today - timedelta(days=43),
                "type_paiement": "lunettes",
                "mode_paiement": "carte",
                "reference_externe": "CB-2025-001312",
                "notes": "Monture + verres antireflets progressifs",
                "valide": True,
            },
            # Paiement conjonctivite - Ndèye Gueye
            {
                "patient": self.patients[5],
                "consultation": self.consultations[5] if len(self.consultations) > 5 else None,
                "montant": Decimal("12000.00"),
                "montant_total_du": Decimal("12000.00"),
                "date": today - timedelta(days=10),
                "type_paiement": "consultation",
                "mode_paiement": "especes",
                "valide": False,
            },
            # Non payé - Moussa Ndiaye (rétinopathie - il y a 60 jours)
            {
                "patient": self.patients[0],
                "consultation": self.consultations[0] if len(self.consultations) > 0 else None,
                "montant": Decimal("0.00"),
                "montant_total_du": Decimal("25000.00"),
                "date": today - timedelta(days=60),
                "type_paiement": "consultation",
                "mode_paiement": "especes",
                "notes": "Patient non solvable au moment de la consultation - relance nécessaire",
                "valide": False,
            },
            # Paiement traitement - Mamadou Diallo
            {
                "patient": self.patients[6],
                "montant": Decimal("8500.00"),
                "montant_total_du": Decimal("15000.00"),
                "date": today - timedelta(days=7),
                "type_paiement": "traitement",
                "mode_paiement": "cheque",
                "reference_externe": "CHQ-00934",
                "notes": "Acompte médicaments - reste 6500 FCFA",
                "valide": False,
            },
        ]

        self.paiements = []
        for data in paiements_data:
            # Éviter les doublons
            existing = Paiement.objects.filter(
                patient=data["patient"],
                montant=data["montant"],
                date=data["date"]
            ).first()
            if not existing:
                p = Paiement.objects.create(created_by=secretaire, **data)
                self.paiements.append(p)
            else:
                self.paiements.append(existing)

        self.stdout.write(f"  {len(self.paiements)} paiements créés/récupérés")

    def _create_sauvegardes(self):
        from apps.sauvegarde.models import Sauvegarde

        admin = self.users["admin"]
        today = timezone.now()

        sauvegardes_data = [
            {
                "date_heure": today - timedelta(days=7),
                "type_sauvegarde": "complete",
                "fichier_path": "backups/sauvegarde_2025-03-24_08h00_complete.bak",
                "taille_octets": 2457600,
                "statut": "reussie",
                "nombre_enregistrements": 847,
                "created_by": admin,
                "message_erreur": "",
            },
            {
                "date_heure": today - timedelta(days=6, hours=12),
                "type_sauvegarde": "incrementale",
                "fichier_path": "backups/sauvegarde_2025-03-24_20h00_incrementale.bak",
                "taille_octets": 45678,
                "statut": "reussie",
                "nombre_enregistrements": 12,
                "created_by": admin,
                "message_erreur": "",
            },
            {
                "date_heure": today - timedelta(days=6),
                "type_sauvegarde": "complete",
                "fichier_path": "backups/sauvegarde_2025-03-25_08h00_complete.bak",
                "taille_octets": 2459136,
                "statut": "reussie",
                "nombre_enregistrements": 851,
                "created_by": admin,
                "message_erreur": "",
            },
            {
                "date_heure": today - timedelta(days=3),
                "type_sauvegarde": "complete",
                "fichier_path": "backups/sauvegarde_2025-03-28_08h00_complete.bak",
                "taille_octets": 2461952,
                "statut": "reussie",
                "nombre_enregistrements": 863,
                "created_by": admin,
                "message_erreur": "",
            },
            {
                "date_heure": today - timedelta(days=2, hours=12),
                "type_sauvegarde": "incrementale",
                "fichier_path": "backups/sauvegarde_2025-03-28_20h00_incrementale.bak",
                "taille_octets": 28672,
                "statut": "echec",
                "nombre_enregistrements": 0,
                "created_by": admin,
                "message_erreur": "Erreur: espace disque insuffisant (espace libre < 100 Mo)",
            },
            {
                "date_heure": today - timedelta(days=1),
                "type_sauvegarde": "complete",
                "fichier_path": "backups/sauvegarde_2025-03-30_08h00_complete.bak",
                "taille_octets": 2465792,
                "statut": "reussie",
                "nombre_enregistrements": 871,
                "created_by": admin,
                "message_erreur": "",
            },
        ]

        for data in sauvegardes_data:
            existing = Sauvegarde.objects.filter(
                fichier_path=data["fichier_path"]
            ).first()
            if not existing:
                Sauvegarde.objects.create(**data)

        self.stdout.write(f"  {Sauvegarde.objects.count()} sauvegardes créées/récupérées")
