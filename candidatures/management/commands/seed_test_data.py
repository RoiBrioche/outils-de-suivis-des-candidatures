from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from datetime import datetime, timedelta
import random
import uuid
import json

from candidatures.models import (
    PeriodeRecherche, Statut, PisteCandidature, 
    Candidature, DocumentCandidature, Contact,
    TypeContrat, Priorite, SourcePriorite, EtatPiste, TypeDocument
)

class Command(BaseCommand):
    help = 'Generate synthetic test data for all models respecting new business rules'

    def add_arguments(self, parser):
        parser.add_argument(
            '--wipe',
            action='store_true',
            help='Delete existing test data before seeding',
        )

    def handle(self, *args, **options):
        if options['wipe']:
            self.wipe_data()
        
        self.stdout.write(self.style.HTTP_INFO('Starting data seeding...'))

        # On utilise une transaction pour garantir l'intégrité (surtout avec les validations clean())
        try:
            with transaction.atomic():
                self.seed_periods()
                self.seed_statuses()
                contacts = self.seed_contacts() # On récupère les contacts pour les lier après
                self.seed_candidatures(contacts)
                self.seed_pistes(contacts)
                self.seed_documents()
            
            self.stdout.write(self.style.SUCCESS('Test data seeded successfully!'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during seeding: {str(e)}'))
            # En mode debug, tu peux vouloir raise e pour voir la stacktrace
            raise e

    def random_date_in_period(self, period):
        start = period.date_debut
        end = period.date_fin or timezone.now().date()
        delta_days = (end - start).days
        return start + timedelta(days=random.randint(0, max(delta_days, 0)))

    def wipe_data(self):
        """Delete all existing test data in correct order to avoid ProtectError"""
        self.stdout.write('Wiping existing data...')
        DocumentCandidature.objects.all().delete()
        PisteCandidature.objects.all().delete() # Suppr pistes avant candidatures/contacts
        Candidature.objects.all().delete()
        Contact.objects.all().delete()
        Statut.objects.all().delete()
        PeriodeRecherche.objects.all().delete()
        self.stdout.write('Data wiped successfully.')

    def seed_periods(self):
        """
        Create PeriodeRecherche instances.
        Attention: Le modèle a une logique complexe dans save() qui ferme les périodes précédentes.
        Il faut les créer de la plus ancienne à la plus récente.
        """
        self.stdout.write('Creating periods...')
        
        # On définit les périodes chronologiquement
        periods_data = [
            {
                "nom": "Recherche 2022",
                "description": "Première période de recherche (Legacy)",
                "date_debut": datetime(2022, 6, 1).date(),
                # date_fin sera géré par la logique du modèle ou forcé ici pour éviter overlap
                "date_fin": datetime(2022, 12, 31).date() 
            },
            {
                "nom": "Recherche 2023",
                "description": "Période de transition",
                "date_debut": datetime(2023, 1, 1).date(),
                "date_fin": datetime(2023, 12, 31).date()
            },
            {
                "nom": "Recherche 2024",
                "description": "Recherche actuelle Fullstack",
                "date_debut": datetime(2024, 1, 1).date(),
                "date_fin": None, # En cours
            }
        ]
        
        for p_data in periods_data:
            # On utilise get_or_create ou create. 
            # Note: Le save() du modèle va gérer 'active' automatiquement basé sur la date.
            p = PeriodeRecherche(**p_data)
            p.save() 
            # On force le clean pour être sûr que tout est valide
            p.clean()

        self.stdout.write(f'Created {PeriodeRecherche.objects.count()} periods')

    def seed_statuses(self):
        self.stdout.write('Creating statuses...')
        statuses = [
            {"nom": "À postuler", "code": "A_POSTULER", "ordre_affichage": 10},
            {"nom": "Candidature envoyée", "code": "ENVOYE", "ordre_affichage": 20},
            {"nom": "Entretien RH", "code": "ENTRETIEN_RH", "ordre_affichage": 30},
            {"nom": "Entretien Technique", "code": "ENTRETIEN_TECH", "ordre_affichage": 40},
            {"nom": "Offre reçue", "code": "OFFRE", "ordre_affichage": 60},
            {"nom": "Refusé", "code": "REFUSE", "ordre_affichage": 80},
            {"nom": "Sans suite", "code": "SANS_SUITE", "ordre_affichage": 90},
        ]
        for data in statuses:
            Statut.objects.get_or_create(code=data['code'], defaults=data)

    def seed_contacts(self):
        """Create Contact instances"""
        self.stdout.write('Creating contacts...')
        
        first_names = ["Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Henry"]
        last_names = ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand"]
        roles = ["RH", "CTO", "Lead Dev", "Talent Acquisition", "CEO"]

        contacts = []
        for _ in range(20): # 20 contacts aléatoires
            prenom = random.choice(first_names)
            nom = random.choice(last_names)
            contact = Contact(
                nom=nom,
                prenom=prenom,
                poste_occupe=random.choice(roles),
                email=f"{prenom.lower()}.{nom.lower()}@example.com",
                telephone=f"06{random.randint(10000000, 99999999)}",
                commentaires="Généré auto"
            )
            contact.save()
            contacts.append(contact)
        
        self.stdout.write(f'Created {Contact.objects.count()} contacts')
        return contacts

    def seed_candidatures(self, available_contacts):
        self.stdout.write('Creating candidatures...')
        
        periods = PeriodeRecherche.objects.all()
        statuses = list(Statut.objects.all())
        companies = ["TechCorp", "StartupXYZ", "DigitalAgency", "FinTech Inc", "Cloud Services"]
        positions = ["Développeur Python", "Backend Dev", "Fullstack Engineer", "DevOps"]
        locations = ["Paris", "Lyon", "Remote", "Bordeaux"]
        
        candidatures_batch = []

        for period in periods:
            count = 15 if period.active else 5
            
            for _ in range(count):
                date_candidature = self.random_date_in_period(period)
                
                # Logique de priorité (Validation rules)
                priorite = random.choice(Priorite.values)
                source_prio = random.choice(SourcePriorite.values)
                date_prio = None
                
                # Règle métier : Si Auto, date obligatoire. Si Manuelle, date optionnelle mais logique.
                if source_prio == SourcePriorite.AUTOMATIQUE:
                    date_prio = date_candidature
                elif source_prio == SourcePriorite.MANUELLE:
                    if random.choice([True, False]):
                        date_prio = date_candidature

                # JSON Contextuel
                context_data = {
                    "tech_stack": ["Django", "React", "Docker"],
                    "salaire_vise": random.randint(40, 70),
                    "remote_policy": "Hybrid"
                }

                candidature = Candidature(
                    periode_recherche=period,
                    statut=random.choice(statuses),
                    entreprise=random.choice(companies),
                    poste=random.choice(positions),
                    localisation=random.choice(locations),
                    contrat=random.choice(TypeContrat.values),
                    canal="LinkedIn",
                    date_candidature=date_candidature,
                    date_statut=date_candidature,
                    priorite=priorite,
                    priorite_source=source_prio,
                    date_priorite=date_prio,
                    statut_contextuel=context_data, # Champ JSONField
                    commentaires="Donnée générée automatiquement"
                )
                
                # On doit sauver pour les M2M (contacts), donc pas de bulk_create pur si on veut lier direct
                # Mais pour la vitesse, on fait save() individuel ici car volume faible
                candidature.full_clean() # Valide les règles métier (clean())
                candidature.save()
                
                # Associer 0 à 2 contacts
                if available_contacts:
                    candidature.contacts.add(*random.sample(available_contacts, k=random.randint(0, 2)))

        self.stdout.write(f'Created {Candidature.objects.count()} candidatures')

    def seed_pistes(self, available_contacts):
        self.stdout.write('Creating pistes...')

        periods = PeriodeRecherche.objects.all()
        # On précharge les candidatures pour faire les liens 'TRANSFORMEE'
        candidatures_by_period = {
            p.id: list(Candidature.objects.filter(periode_recherche=p))
            for p in periods
        }

        companies = ["InnovateTech", "Future Systems", "NextGen Software", "Alpha Corp"]
        positions = ["Senior Developer", "Tech Lead", "Architect", "Lead Python"]
        sources = ["AngelList", "Hired", "Otta", "Welcome to the Jungle"]

        for period in periods:
            count = 20 if period.active else 5

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

                # Règle métier : Si TRANSFORMEE, il FAUT une candidature
                if etat == EtatPiste.TRANSFORMEE:
                    candidates = candidatures_by_period.get(period.id, [])
                    if candidates:
                        piste.candidature = random.choice(candidates)
                    else:
                        # Si pas de candidature dispo, on change l'état pour éviter l'erreur de validation
                        piste.etat = EtatPiste.ABANDONNEE
                
                piste.full_clean()
                piste.save()

                # Associer des contacts à la piste
                if available_contacts:
                    piste.contacts.add(*random.sample(available_contacts, k=random.randint(0, 2)))

        self.stdout.write(f'Created {PisteCandidature.objects.count()} pistes')

    def seed_documents(self):
        """Create DocumentCandidature instances"""
        self.stdout.write('Creating documents...')
        
        candidatures = list(Candidature.objects.all())
        filenames = {
            TypeDocument.CV: ["CV_2024.pdf", "Resume.pdf"],
            TypeDocument.LETTRE_MOTIVATION: ["LM.pdf", "Cover_Letter.pdf"],
            TypeDocument.PORTFOLIO: ["Portfolio.pdf"],
            TypeDocument.TEST_TECHNIQUE: ["Test_Result.zip"],
            TypeDocument.AUTRE: ["Diplome.pdf"]
        }
        
        documents = []
        for candidature in candidatures:
            num_docs = random.randint(0, 3)
            for _ in range(num_docs):
                doc_type = random.choice(TypeDocument.values)
                fname = random.choice(filenames.get(doc_type, ["doc.pdf"]))
                
                doc = DocumentCandidature(
                    candidature=candidature,
                    type_document=doc_type,
                    nom_fichier=fname,
                    chemin_fichier=f"uploads/{candidature.id}/{fname}",
                    mime_type="application/pdf",
                    taille=random.randint(50000, 5000000),
                    commentaire="Auto-generated"
                )
                documents.append(doc)
        
        DocumentCandidature.objects.bulk_create(documents)
        self.stdout.write(f'Created {DocumentCandidature.objects.count()} documents')