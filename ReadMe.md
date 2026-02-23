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
pip install -r requirements-dev.txt  # For development tools
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

## 🧪 Development Tools & CI

This project includes a complete CI/CD pipeline with quality assurance tools.

### Local Development Commands

#### Code Quality
```bash
# Format code with black
black .

# Check code formatting (without modifying)
black --check .

# Lint code with ruff
ruff check .

# Fix linting issues automatically
ruff check . --fix
```

#### Testing
```bash
# Run all tests with coverage
pytest --cov=.

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_django_startup.py
```

#### Security
```bash
# Security scan for code vulnerabilities
bandit -r .

# Check for known vulnerabilities in dependencies
pip-audit
```

#### Coverage Report
```bash
# Generate HTML coverage report
pytest --cov=. --cov-report=html

# View coverage report
# Open htmlcov/index.html in your browser
```

### CI/CD Pipeline

The project includes GitHub Actions workflow (`.github/workflows/ci.yml`) that automatically runs on:
- Push to `main`, `master`, or `develop` branches
- Pull requests to these branches

**Pipeline Steps:**
1. **Code Quality**: ruff linting + black formatting check
2. **Security**: bandit (code security) + pip-audit (dependency vulnerabilities)
3. **Testing**: pytest with coverage reporting
4. **Coverage**: Optional upload to Codecov (doesn't fail CI if coverage is low)

**Quality Standards:**
- Line length: 88 characters (black)
- Linting rules: E, F, I, UP, B (ruff)
- Test settings: `job_tracker.settings.test`
- Coverage threshold: 0% (non-blocking for now)

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
