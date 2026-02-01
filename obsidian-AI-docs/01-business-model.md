# 01-business-model.md

## Entities

### PeriodeRecherche
- Represents a job search period
- A period groups multiple job applications
- One active period at a time (constraint)
- Fields: id, nom, description, date_debut, date_fin, active, created_at, updated_at

### Candidature
- Represents a single job application
- Belongs to exactly one PeriodeRecherche
- Has exactly one Statut
- Core fields:
  - entreprise (required)
  - poste (required)
  - date_candidature (required)
  - statut (FK to Statut, required)
  - localisation (optional)
  - contrat (enum TypeContrat, optional)
  - canal (optional)
  - commentaires (optional)
  - statut_contextuel (JSON, optional)
  - date_statut (required)
  - priorite (enum Priorite, optional)
  - priorite_source (enum SourcePriorite, optional)
  - date_priorite (optional)

### Statut
- Referential entity for application status
- Fields: id, nom (unique), code (unique), actif (default true), ordre_affichage, created_at
- Default statuses: EN_ATTENTE, EN_COURS, REFUSEE, CLOTUREE

### PisteCandidature
- Represents an opportunity before transformation to candidature
- Belongs to exactly one PeriodeRecherche
- May optionally reference one Candidature (when transformed)
- Fields:
  - entreprise (required)
  - poste_cible (optional)
  - source (optional)
  - contact (optional)
  - url_annonce (optional)
  - commentaires (optional)
  - etat (enum EtatPiste, required)
  - candidature (FK to Candidature, optional)

### DocumentCandidature
- Represents a document associated with a candidature
- Belongs to exactly one Candidature
- Fields:
  - type_document (enum TypeDocument, required)
  - nom_fichier (required)
  - chemin_fichier (string, required)
  - mime_type (optional)
  - taille (optional)
  - commentaire (optional)
  - date_ajout (required)

## Relationships
- PeriodeRecherche 1 → N Candidature
- PeriodeRecherche 1 → N PisteCandidature
- Statut 1 → N Candidature
- Candidature 1 → N DocumentCandidature
- PisteCandidature 0..1 → 1 Candidature (optional, one-way)

## Business Rules
- A candidature cannot exist without a period
- Only one period can be active at a time
- Manual priority overrides automatic priority
- A piste with etat=TRANSFORMEE must have an associated candidature
- Status values are constrained by enums

## Enumerations
- TypeContrat: CDI, CDD, ALTERNANCE, STAGE, FREELANCE, AUTRE
- Priorite: FAIBLE, NORMALE, ELEVEE
- SourcePriorite: AUTOMATIQUE, MANUELLE
- EtatPiste: A_ETUDIER, A_CONTACTER, EN_PREPARATION, ABANDONNEE, TRANSFORMEE
- TypeDocument: CV, LETTRE_MOTIVATION, AUTRE
