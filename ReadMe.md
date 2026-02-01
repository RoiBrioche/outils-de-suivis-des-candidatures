# Job Application Tracker (MVP)

## 📌 Overview

**Job Application Tracker** is a Django MVP application for managing and tracking job applications.  
It allows you to:  
- Add, modify, and delete job applications (CRUD)  
- View and filter applications on a main interface  
- Manage application periods  
- View simple statistics  

The project follows domain-driven design principles with strict server-side validation and business rule enforcement.

---

## 🛠️ Technology Stack

- **Backend**: Python + Django 5.2+  
- **Database**: SQLite (MVP)  
- **Architecture**: Domain-driven Django apps  
- **Validation**: Django ModelForms with business rules  
- **UI**: Bootstrap 5 for minimal styling

---

##  Project Structure

```
job-tracker/
│
├─ README.md
├─ LICENSE
├─ .gitignore
├─ requirements.txt
├─ manage.py
├─ obsidian-AI-docs/           # project documentation for AI
│   ├─ 00-context.md
│   ├─ 01-business-model.md
│   ├─ 02-architecture.md
│   ├─ 03-validation-errors.md
│   └─ 04-ui-scope.md
├─ job_tracker/                 # Django project configuration
│   ├─ __init__.py
│   ├─ settings.py
│   ├─ urls.py
│   ├─ wsgi.py
│   └─ asgi.py
├─ candidatures/                # Django app for job applications
│   ├─ __init__.py
│   ├─ admin.py
│   ├─ apps.py
│   ├─ models.py
│   ├─ views.py
│   ├─ forms.py
│   ├─ urls.py
│   └─ templates/candidatures/
│       ├─ base.html
│       ├─ candidature_list.html
│       ├─ candidature_form.html
│       ├─ candidature_detail.html
│       ├─ candidature_confirm_delete.html
│       ├─ periode_list.html
│       ├─ periode_form.html
│       ├─ periode_confirm_delete.html
│       ├─ piste_list.html
│       ├─ piste_form.html
│       └─ piste_confirm_delete.html
├─ venv/                       # virtual environment
└─ db.sqlite3                  # SQLite database (created after migrate)
```

---

## 🚀 Installation

1. **Clone the repository**  
```bash
git clone <repository-url>
cd outils-de-suivis-des-candidatures
```

2. **Create and activate virtual environment**  
```bash
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # Linux / macOS
```

3. **Install dependencies**  
```bash
pip install -r requirements.txt
```

4. **Initialize the database**  
```bash
python manage.py migrate
```

5. **Create superuser (optional, for admin access)**  
```bash
python manage.py createsuperuser
```

6. **Start the development server**  
```bash
python manage.py runserver
```

7. **Access the application**  
- Main application: http://127.0.0.1:8000/
- Admin interface: http://127.0.0.1:8000/admin/

---

## Features

### Core Functionality
- **Job Application Management**: Full CRUD operations for job applications
- **Period Organization**: Group applications by search periods
- **Lead Tracking**: Optional source/lead tracking for applications
- **Search & Filter**: Search by company/position, filter by status and period
- **Status Management**: Constrained status transitions (En attente, En cours, Entretien planifié, Refusé, Accepté, Retiré)

### Business Rules
- Only one active search period at a time
- Application dates must belong to their period
- Required fields enforced server-side
- Cascade delete: deleting a period removes its applications

### Admin Interface
- Full Django admin integration for all models
- Superuser access for data management
- Debug-friendly interface

---

## Architecture

### Domain Models
- **PeriodeRecherche**: Job search periods with one-active constraint
- **Candidature**: Individual job applications with status tracking
- **PisteCandidature**: Optional lead/source tracking

### Validation Layer
- Django ModelForms with custom clean() methods
- Business rule enforcement at model and form level
- Structured ValidationError responses
- No silent failures

### Views & URLs
- Class-based views for all CRUD operations
- RESTful URL patterns
- Pagination support
- Search functionality

---

## Documentation

The `obsidian-AI-docs/` folder contains authoritative project documentation:
- **00-context.md**: Project scope and constraints
- **01-business-model.md**: Domain entities and relationships
- **02-architecture.md**: Technical architecture and patterns
- **03-validation-errors.md**: Validation strategy and error handling
- **04-ui-scope.md**: UI requirements and constraints

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
