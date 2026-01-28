# 02-architecture.md

## Backend
- Framework: Django
- Structure:
  - apps/ (domain-based Django apps)
  - models.py for ORM definitions
  - forms.py or serializers.py for validation
  - views.py using class-based views

## Database
- SQLite for MVP
- ORM-managed schema
- Migration-ready for PostgreSQL

## Application Flow
- HTTP request → View → Validation → ORM → Response
- All writes pass through Django validation layer

## Error Strategy
- No silent failures
- Validation errors returned as structured responses
- System errors logged, generic message returned
