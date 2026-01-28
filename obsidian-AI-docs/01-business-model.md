# 01-business-model.md

## Entities

### PeriodeRecherche
- Represents a job search period
- A period groups multiple job applications
- One active period at a time (constraint)

### Candidature
- Represents a single job application
- Belongs to exactly one PeriodeRecherche
- Core fields (implicit, required):
  - company
  - position
  - application_date
  - status

### PisteCandidature
- Optional lead or source for a candidature
- Linked to zero or more candidatures

## Relationships
- PeriodeRecherche 1 → N Candidature
- PisteCandidature 1 → N Candidature (optional)

## Business Rules
- A candidature cannot exist without a period
- Deleting a period deletes its candidatures
- Status values are constrained (enum-like)
