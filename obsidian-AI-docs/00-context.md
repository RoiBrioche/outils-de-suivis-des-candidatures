# 00-context.md

## Project Scope
- Application: Job application tracking (MVP)
- Backend: Django
- Database: SQLite (MVP only)
- Architecture: Server-rendered or API-driven Django app
- Primary entity: Job Application (Candidature)

## Core Capabilities
- CRUD operations on job applications
- Period-based organization of applications
- Simple statistics (counts, status distribution)
- Server-side validation and error handling

## Non-Goals (MVP)
- Authentication / multi-user
- External integrations
- Advanced analytics
- Asynchronous processing

## Constraints
- All business rules enforced server-side
- Data integrity prioritized over UI flexibility
- Optimized for rapid iteration and code generation
