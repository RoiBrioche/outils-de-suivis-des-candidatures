"""
Management command to generate synthetic test data for all models.
Respects all model validation rules and business constraints.
Deterministic and repeatable data generation.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import random
import uuid

from candidatures.models import (
    PeriodeRecherche, Statut, PisteCandidature, 
    Candidature, DocumentCandidature, TypeContrat, 
    Priorite, SourcePriorite, EtatPiste, TypeDocument
)


class Command(BaseCommand):
    help = 'Generate synthetic test data for all models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--wipe',
            action='store_true',
            help='Delete existing test data before seeding',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output during seeding',
        )

    def handle(self, *args, **options):
        
        if options['wipe']:
            self.wipe_data()
        
        with transaction.atomic():
            self.seed_periods()
            self.seed_statuses()
            self.seed_candidatures()
            self.seed_pistes()
            self.seed_documents()
        
        self.stdout.write(
            self.style.SUCCESS('Test data seeded successfully!')
        )

    def random_date_in_period(self, period):
        start = period.date_debut
        end = period.date_fin or timezone.now().date()
        delta_days = (end - start).days
        return start + timedelta(days=random.randint(0, max(delta_days, 0)))


    def wipe_data(self):
        """Delete all existing test data in correct order"""
        self.stdout.write('Wiping existing data...')
        DocumentCandidature.objects.all().delete()
        PisteCandidature.objects.all().delete()
        Candidature.objects.all().delete()
        Statut.objects.all().delete()
        PeriodeRecherche.objects.all().delete()
        self.stdout.write('Data wiped successfully.')

    def seed_periods(self):
        """Create PeriodeRecherche instances"""
        self.stdout.write('Creating periods...')
        
        # Active period (current)
        active_period = PeriodeRecherche.objects.create(
            nom="Recherche 2024",
            description="Période de recherche d'emploi active",
            date_debut=datetime(2024, 1, 1).date(),
            date_fin=None,
            active=True
        )
        
        # Inactive periods
        inactive_periods = [
            {
                "nom": "Recherche 2023",
                "description": "Période de recherche précédente",
                "date_debut": datetime(2023, 1, 1).date(),
                "date_fin": datetime(2023, 12, 31).date(),
                "active": False
            },
            {
                "nom": "Recherche 2022",
                "description": "Première période de recherche",
                "date_debut": datetime(2022, 6, 1).date(),
                "date_fin": datetime(2022, 12, 31).date(),
                "active": False
            }
        ]
        
        for period_data in inactive_periods:
            PeriodeRecherche.objects.create(**period_data)
        
        self.stdout.write(f'Created {PeriodeRecherche.objects.count()} periods')

    def seed_statuses(self):
        """Create Statut instances"""
        self.stdout.write('Creating statuses...')
        
        statuses = [
            {"nom": "À postuler", "code": "A_POSTULER", "ordre_affichage": 10},
            {"nom": "Candidature envoyée", "code": "ENVOYE", "ordre_affichage": 20},
            {"nom": "Entretien téléphonique", "code": "ENTRETIEN_PHONE", "ordre_affichage": 30},
            {"nom": "Entretien technique", "code": "ENTRETIEN_TECH", "ordre_affichage": 40},
            {"nom": "Entretien final", "code": "ENTRETIEN_FINAL", "ordre_affichage": 50},
            {"nom": "Offre reçue", "code": "OFFRE", "ordre_affichage": 60},
            {"nom": "Accepté", "code": "ACCEPTE", "ordre_affichage": 70},
            {"nom": "Refusé", "code": "REFUSE", "ordre_affichage": 80},
            {"nom": "Sans suite", "code": "SANS_SUITE", "ordre_affichage": 90},
        ]
        
        for status_data in statuses:
            Statut.objects.create(**status_data)
        
        self.stdout.write(f'Created {Statut.objects.count()} statuses')

    def seed_candidatures(self):
        self.stdout.write('Creating candidatures...')
        
        periods = PeriodeRecherche.objects.all()
        statuses = list(Statut.objects.all())

        companies = [
            "TechCorp", "StartupXYZ", "DigitalAgency", "FinTech Inc",
            "Cloud Services", "AI Innovations", "Data Analytics Co"
        ]

        positions = [
            "Développeur Python", "Développeur Django",
            "Backend Developer", "Software Engineer"
        ]

        locations = ["Paris", "Lyon", "Remote"]
        sources = ["LinkedIn", "Indeed", "APEC", "Site entreprise"]

        candidatures = []

        for period in periods:
            # Volume différent selon période
            count = 15 if period.active else random.randint(5, 10)

            for _ in range(count):
                date_candidature = self.random_date_in_period(period)

                # Statuts plus "terminaux" pour périodes passées
                if period.active:
                    status = random.choice(statuses)
                else:
                    status = random.choice([
                        s for s in statuses
                        if s.code in {"REFUSE", "SANS_SUITE", "ACCEPTE"}
                    ])

                candidature = Candidature(
                    periode_recherche=period,
                    statut=status,
                    entreprise=random.choice(companies),
                    poste=random.choice(positions),
                    localisation=random.choice(locations),
                    contrat=random.choice(list(TypeContrat.values)),
                    canal=random.choice(sources),
                    date_candidature=date_candidature,
                    date_statut=date_candidature,
                    commentaires="Donnée générée automatiquement"
                )

                candidatures.append(candidature)

        Candidature.objects.bulk_create(candidatures)
        self.stdout.write(f'Created {Candidature.objects.count()} candidatures')


    def seed_pistes(self):
        self.stdout.write('Creating pistes...')

        periods = PeriodeRecherche.objects.all()
        candidatures_by_period = {
            p.id: list(Candidature.objects.filter(periode_recherche=p))
            for p in periods
        }

        companies = ["InnovateTech", "Future Systems", "NextGen Software"]
        positions = ["Senior Developer", "Tech Lead", "Architect"]
        sources = ["AngelList", "Hired", "Otta"]

        pistes = []

        for period in periods:
            count = 20 if period.active else random.randint(5, 8)

            for _ in range(count):
                etat = random.choice(list(EtatPiste.values))

                piste = PisteCandidature(
                    periode_recherche=period,
                    entreprise=random.choice(companies),
                    poste_cible=random.choice(positions),
                    source=random.choice(sources),
                    url_annonce=f"https://example.com/job/{uuid.uuid4().hex[:8]}",
                    commentaires="Piste générée automatiquement",
                    etat=etat
                )

                # Association uniquement si transformée
                if etat == EtatPiste.TRANSFORMEE:
                    candidates = candidatures_by_period.get(period.id, [])
                    if candidates:
                        piste.candidature = random.choice(candidates)

                pistes.append(piste)

        PisteCandidature.objects.bulk_create(pistes)
        self.stdout.write(f'Created {PisteCandidature.objects.count()} pistes')


    def seed_documents(self):
        """Create DocumentCandidature instances"""
        self.stdout.write('Creating documents...')
        
        candidatures = list(Candidature.objects.all())
        
        document_types = list(TypeDocument.values)
        
        filenames = {
            TypeDocument.CV: ["CV_Brieuc_2024.pdf", "Resume_Brieuc.pdf", "CV_Tech_Brieuc.pdf"],
            TypeDocument.LETTRE_MOTIVATION: ["Lettre_Motivation.pdf", "Cover_Letter.pdf", "LM_Tech.pdf"],
            TypeDocument.PORTFOLIO: ["Portfolio_Brieuc.pdf", "Projects_Showcase.pdf"],
            TypeDocument.TEST_TECHNIQUE: ["Test_Technique_Resultat.pdf", "Coding_Challenge.pdf"],
            TypeDocument.AUTRE: ["Certification.pdf", "Reference_Letter.pdf", "Diploma.pdf"]
        }
        
        documents = []
        for candidature in candidatures:
            # Each candidature gets 1-3 documents
            num_docs = random.randint(1, 3)
            
            for i in range(num_docs):
                doc_type = random.choice(document_types)
                filename_options = filenames.get(doc_type, ["Document.pdf"])
                filename = random.choice(filename_options)
                
                document = DocumentCandidature(
                    candidature=candidature,
                    type_document=doc_type,
                    nom_fichier=filename,
                    chemin_fichier=f"documents/{candidature.id}/{filename}",
                    mime_type="application/pdf",
                    taille=random.randint(100000, 2000000),  # 100KB to 2MB
                    commentaire=f"Document ajouté le {timezone.now().date()}"
                )
                documents.append(document)
        
        DocumentCandidature.objects.bulk_create(documents)
        self.stdout.write(f'Created {DocumentCandidature.objects.count()} documents')
