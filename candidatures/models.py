import uuid
from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


class TypeContrat(models.TextChoices):
    CDI = "CDI", "CDI"
    CDD = "CDD", "CDD"
    ALTERNANCE = "ALTERNANCE", "Alternance"
    STAGE = "STAGE", "Stage"
    FREELANCE = "FREELANCE", "Freelance"
    AUTRE = "AUTRE", "Autre"
    INTERIM = "INTERIM", "Intérim"


class Priorite(models.TextChoices):
    FAIBLE = "FAIBLE", "Faible"
    NORMALE = "NORMALE", "Normale"
    ELEVEE = "ELEVEE", "Élevée"


class SourcePriorite(models.TextChoices):
    MANUELLE = "MANUELLE", "Manuelle"
    AUTOMATIQUE = "AUTOMATIQUE", "Automatique"


class EtatPiste(models.TextChoices):
    A_ETUDIER = "A_ETUDIER", "À étudier"
    A_CONTACTER = "A_CONTACTER", "À contacter"
    EN_PREPARATION = "EN_PREPARATION", "En préparation"
    ABANDONNEE = "ABANDONNEE", "Abandonnée"
    TRANSFORMEE = "TRANSFORMEE", "Transformée"


class TypeDocument(models.TextChoices):
    CV = "CV", "CV"
    LETTRE_MOTIVATION = "LETTRE_MOTIVATION", "Lettre de motivation"
    PORTFOLIO = "PORTFOLIO", "Portfolio"
    TEST_TECHNIQUE = "TEST_TECHNIQUE", "Test technique"
    AUTRE = "AUTRE", "Autre"


class PeriodeRecherche(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=200, verbose_name="Nom de la période")
    description = models.TextField(blank=True, verbose_name="Description")
    date_debut = models.DateField(default=timezone.now, verbose_name="Date de début")
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    active = models.BooleanField(default=True, verbose_name="Période active")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Période de recherche"
        verbose_name_plural = "Périodes de recherche"
        ordering = ["-date_debut"]

    def __str__(self):
        return f"{self.nom} ({self.date_debut} - {self.date_fin or 'en cours'})"

    def clean(self):
        if self.date_fin and self.date_debut and self.date_fin < self.date_debut:
            raise ValidationError(
                {
                    "date_fin": "La date de fin ne peut pas être antérieure à la date de début."
                }
            )

        # Check for overlaps with existing closed periods
        existing_periods = PeriodeRecherche.objects.exclude(pk=self.pk).filter(
            date_fin__isnull=False
        )

        for period in existing_periods:
            # Standard overlap logic: StartA <= EndB and EndA >= StartB
            overlap_condition = self.date_debut <= period.date_fin and (
                self.date_fin is None or self.date_fin >= period.date_debut
            )

            if overlap_condition:
                raise ValidationError(
                    {
                        "date_debut": f"La date de début chevauche la période '{period.nom}' qui se termine le {period.date_fin}."
                    }
                )

    def save(self, *args, **kwargs):
        from django.utils import timezone

        today = timezone.now().date()

        # Check if this period covers today
        covers_today = self.date_debut <= today and (
            self.date_fin is None or today <= self.date_fin
        )

        # Check if a newer period exists (excluding self)
        has_newer_period = (
            PeriodeRecherche.objects.filter(date_debut__gt=self.date_debut)
            .exclude(pk=self.pk)
            .exists()
        )

        # Set active status: only active if covers today AND no newer period exists
        self.active = covers_today and not has_newer_period

        # If this period is active, deactivate all other periods and close them properly
        if self.active:
            active_periods = PeriodeRecherche.objects.filter(active=True).exclude(
                pk=self.pk
            )
            for old_period in active_periods:
                old_period.active = False

                # Only set end date if new period starts after old period and old period has no end date
                update_fields = ["active"]
                if (
                    old_period.date_fin is None
                    and self.date_debut > old_period.date_debut
                ):
                    old_period.date_fin = self.date_debut - timedelta(days=1)
                    update_fields.append("date_fin")

                old_period.save(update_fields=update_fields)

        self.clean()
        super().save(*args, **kwargs)


class Statut(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100, unique=True, verbose_name="Nom du statut")
    code = models.CharField(
        max_length=50, unique=True, default="", verbose_name="Code technique"
    )
    actif = models.BooleanField(default=True, verbose_name="Actif")
    ordre_affichage = models.PositiveIntegerField(
        default=0, verbose_name="Ordre d'affichage"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    class Meta:
        verbose_name = "Statut"
        verbose_name_plural = "Statuts"
        ordering = ["ordre_affichage", "nom"]

    def __str__(self):
        return self.nom


class Contact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=200, verbose_name="Nom")
    prenom = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Prénom"
    )
    poste_occupe = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Poste occupé"
    )
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    telephone = models.CharField(
        max_length=20, blank=True, null=True, verbose_name="Téléphone"
    )
    linkedin_url = models.URLField(blank=True, null=True, verbose_name="URL LinkedIn")
    commentaires = models.TextField(blank=True, null=True, verbose_name="Commentaires")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Contact"
        verbose_name_plural = "Contacts"
        ordering = ["nom", "prenom"]
        indexes = [
            models.Index(fields=["nom"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        if self.prenom and self.poste_occupe:
            return f"{self.prenom} {self.nom} ({self.poste_occupe})"
        elif self.prenom:
            return f"{self.prenom} {self.nom}"
        elif self.poste_occupe:
            return f"{self.nom} ({self.poste_occupe})"
        return self.nom

    @property
    def nom_complet(self):
        if self.prenom:
            return f"{self.prenom} {self.nom}"
        return self.nom


class PisteCandidature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periode_recherche = models.ForeignKey(
        PeriodeRecherche,
        on_delete=models.CASCADE,
        related_name="pistes",
        verbose_name="Période de recherche",
    )
    entreprise = models.CharField(max_length=200, default="", verbose_name="Entreprise")
    poste_cible = models.CharField(
        max_length=200, blank=True, verbose_name="Poste ciblé"
    )
    source = models.CharField(max_length=200, blank=True, verbose_name="Source")
    url_annonce = models.URLField(blank=True, verbose_name="URL de l'annonce")
    commentaires = models.TextField(blank=True, verbose_name="Commentaires")
    etat = models.CharField(
        max_length=20,
        choices=EtatPiste.choices,
        default=EtatPiste.A_ETUDIER,
        verbose_name="État",
    )
    candidature = models.ForeignKey(
        "Candidature",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pistes_source",
        verbose_name="Candidature associée",
    )
    contacts = models.ManyToManyField(
        "Contact",
        blank=True,
        related_name="pistes_candidature",
        verbose_name="Contacts",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Piste de candidature"
        verbose_name_plural = "Pistes de candidature"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.entreprise} - {self.get_etat_display()}"

    def clean(self):
        if self.etat == EtatPiste.TRANSFORMEE and not self.candidature:
            raise ValidationError(
                {"etat": "Une piste transformée doit être associée à une candidature."}
            )


class Candidature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    periode_recherche = models.ForeignKey(
        PeriodeRecherche,
        on_delete=models.CASCADE,
        related_name="candidatures",
        verbose_name="Période de recherche",
    )
    statut = models.ForeignKey(
        Statut,
        on_delete=models.PROTECT,
        related_name="candidatures",
        verbose_name="Statut",
    )
    entreprise = models.CharField(max_length=200, verbose_name="Entreprise")
    poste = models.CharField(max_length=200, verbose_name="Poste")
    localisation = models.CharField(
        max_length=200, blank=True, verbose_name="Localisation"
    )
    contrat = models.CharField(
        max_length=20,
        choices=TypeContrat.choices,
        blank=True,
        verbose_name="Type de contrat",
    )
    canal = models.CharField(max_length=200, blank=True, verbose_name="Canal")
    date_candidature = models.DateField(
        default=timezone.now, verbose_name="Date de candidature"
    )
    commentaires = models.TextField(blank=True, verbose_name="Commentaires")
    statut_contextuel = models.JSONField(
        null=True, blank=True, verbose_name="Informations contextuelles du statut"
    )
    date_statut = models.DateField(default=timezone.now, verbose_name="Date du statut")
    priorite = models.CharField(
        max_length=20, choices=Priorite.choices, blank=True, verbose_name="Priorité"
    )
    priorite_source = models.CharField(
        max_length=20,
        choices=SourcePriorite.choices,
        blank=True,
        verbose_name="Source de la priorité",
    )
    date_priorite = models.DateField(
        null=True, blank=True, verbose_name="Date de la priorité"
    )
    contacts = models.ManyToManyField(
        "Contact", blank=True, related_name="candidatures", verbose_name="Contacts"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")

    class Meta:
        verbose_name = "Candidature"
        verbose_name_plural = "Candidatures"
        ordering = ["-date_candidature"]
        indexes = [
            models.Index(fields=["date_candidature"]),
            models.Index(fields=["entreprise"]),
            models.Index(fields=["poste"]),
            models.Index(fields=["priorite"]),
        ]

    def __str__(self):
        return f"{self.poste} chez {self.entreprise}"

    def clean(self):
        if self.periode_recherche:
            if self.date_candidature < self.periode_recherche.date_debut:
                raise ValidationError(
                    {
                        "date_candidature": "La date de candidature ne peut pas être antérieure à la date de début de la période."
                    }
                )
            if (
                self.periode_recherche.date_fin
                and self.date_candidature > self.periode_recherche.date_fin
            ):
                raise ValidationError(
                    {
                        "date_candidature": "La date de candidature ne peut pas être postérieure à la date de fin de la période."
                    }
                )

        # Business rule: manual priority overrides automatic priority
        if self.priorite and self.priorite_source == SourcePriorite.MANUELLE:
            # Manual priority is always valid
            pass
        elif self.priorite and self.priorite_source == SourcePriorite.AUTOMATIQUE:
            # Automatic priority should have a date
            if not self.date_priorite:
                raise ValidationError(
                    {
                        "date_priorite": "Une priorité automatique doit avoir une date d'application."
                    }
                )

        # If priority is set, source must be set
        if self.priorite and not self.priorite_source:
            raise ValidationError(
                {"priorite_source": "La source de la priorité doit être spécifiée."}
            )

        # If priority source is set, priority must be set
        if self.priorite_source and not self.priorite:
            raise ValidationError(
                {"priorite": "Le niveau de priorité doit être spécifié."}
            )


class DocumentCandidature(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidature = models.ForeignKey(
        Candidature,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Candidature",
    )
    type_document = models.CharField(
        max_length=20, choices=TypeDocument.choices, verbose_name="Type de document"
    )
    nom_fichier = models.CharField(max_length=255, verbose_name="Nom du fichier")
    chemin_fichier = models.CharField(
        max_length=500, default="", verbose_name="Chemin du fichier"
    )
    mime_type = models.CharField(max_length=100, blank=True, verbose_name="Type MIME")
    taille = models.PositiveIntegerField(
        null=True, blank=True, verbose_name="Taille (octets)"
    )
    commentaire = models.TextField(blank=True, verbose_name="Commentaire")
    date_ajout = models.DateTimeField(auto_now_add=True, verbose_name="Date d'ajout")

    class Meta:
        verbose_name = "Document de candidature"
        verbose_name_plural = "Documents de candidature"
        ordering = ["-date_ajout"]

    def __str__(self):
        return f"{self.nom_fichier} - {self.candidature}"
