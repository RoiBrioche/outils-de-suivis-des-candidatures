# Django Job Tracker - Development & Testing Setup

This document provides a complete guide for setting up and using the development/testing environment for the Django Job Tracker application.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Initial Setup (Test Environment)
```bash
# Set environment to test settings
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test

# Run migrations
python manage.py migrate

# Create superuser
python manage.py create_superuser

# Seed test data
python manage.py seed_test_data

# Start development server
python manage.py runserver
```

Access admin at: http://127.0.0.1:8000/admin/
- Username: `Brieuc`
- Password: `password`

## 📁 Settings Structure

The project uses a split settings configuration:

- `job_tracker/settings/base.py` - Common settings for all environments
- `job_tracker/settings/dev.py` - Development-specific settings
- `job_tracker/settings/test.py` - Test-specific settings (isolated database)

### Environment Switching

**For Development:**
```bash
export DJANGO_SETTINGS_MODULE=job_tracker.settings.dev
```

**For Testing:**
```bash
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test
```

**Windows PowerShell:**
```powershell
$env:DJANGO_SETTINGS_MODULE = "job_tracker.settings.test"
```

## 🔄 Fast Reset Workflow

Complete database reset and re-seeding in ≤3 commands:

### Option 1: Test Environment Reset
```bash
# 1. Set test environment
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test

# 2. Drop database and recreate
rm db_test.sqlite3
python manage.py migrate

# 3. Create superuser and seed data
python manage.py create_superuser && python manage.py seed_test_data
```

### Option 2: Development Environment Reset
```bash
# 1. Set dev environment
export DJANGO_SETTINGS_MODULE=job_tracker.settings.dev

# 2. Drop database and recreate
rm db_dev.sqlite3
python manage.py migrate

# 3. Create superuser and seed data
python manage.py create_superuser && python manage.py seed_test_data
```

### Option 3: One-Liner Reset (Test)
```bash
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test && rm db_test.sqlite3 && python manage.py migrate && python manage.py create_superuser && python manage.py seed_test_data
```

## 🛠️ Management Commands

### create_superuser
Creates the default development superuser (Brieuc/password).

```bash
# Create superuser (idempotent)
python manage.py create_superuser

# Force recreation if user exists
python manage.py create_superuser --force
```

**Safety:** Only works in DEBUG mode with dev/test settings.

### seed_test_data
Generates realistic synthetic data for all models.

```bash
# Seed data (preserves existing)
python manage.py seed_test_data

# Wipe existing data and recreate
python manage.py seed_test_data --wipe

# Verbose output
python manage.py seed_test_data --verbose
```

**Generated Data:**
- 3 PeriodeRecherche (1 active, 2 inactive)
- 9 Statut with proper display order
- 15 Candidature with various statuses and priorities
- 20 PisteCandidature (mixed states, some transformed)
- 30+ DocumentCandidature linked to candidatures

All data respects model validation rules and business constraints.

## 🎯 Development Workflow

### Daily Development
```bash
# 1. Set environment
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test

# 2. Start server
python manage.py runserver

# 3. Access admin interface
# http://127.0.0.1:8000/admin/
```

### Testing Broken UI/Forms
```bash
# 1. Reset to clean state
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test
rm db_test.sqlite3
python manage.py migrate
python manage.py create_superuser
python manage.py seed_test_data

# 2. Test through admin interface
# - Create/edit PeriodeRecherche
# - Create/edit Statut
# - Create/edit Candidature (test validation)
# - Create/edit PisteCandidature
# - Create/edit DocumentCandidature
```

### Debugging Model Issues
```bash
# 1. Access Django shell
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test
python manage.py shell

# 2. Test model creation/validation
from candidatures.models import *
from django.core.exceptions import ValidationError

# Test specific scenarios
period = PeriodeRecherche.objects.get(active=True)
candidature = Candidature.objects.first()
# ... test your scenarios
```

## 🏗️ Project Structure

```
job_tracker/
├── settings/
│   ├── __init__.py
│   ├── base.py          # Common settings
│   ├── dev.py           # Development settings
│   └── test.py          # Test settings
└── settings.py          # Legacy (can be removed)

candidatures/
├── management/
│   └── commands/
│       ├── create_superuser.py
│       └── seed_test_data.py
└── models.py            # Domain models (unchanged)
```

## 📊 Database Files

- `db_dev.sqlite3` - Development database
- `db_test.sqlite3` - Test database (isolated)
- `db.sqlite3` - Legacy database (not used with new settings)

## 🔧 Django Admin Interface

The project includes `django-admin-interface` for an improved admin experience:

- Modern, clean interface
- Better responsive design
- Enhanced form layouts
- Improved navigation

Features are automatically enabled when using dev/test settings.

## ⚠️ Important Notes

### Safety Features
- Superuser creation only works in DEBUG mode
- Test database is completely isolated
- Management commands include safety checks

### Model Validation
- All synthetic data respects `clean()` methods
- Business rules are enforced (e.g., single active period)
- Date constraints are respected
- Priority rules are followed

### Reproducibility
- Data generation is deterministic
- Same seed produces consistent results
- Commands are idempotent where possible

## 🐛 Troubleshooting

### "Settings not found" Error
```bash
# Ensure DJANGO_SETTINGS_MODULE is set correctly
export DJANGO_SETTINGS_MODULE=job_tracker.settings.test
```

### "Superuser already exists" Warning
This is normal - the command is idempotent. Use `--force` to recreate.

### Migration Issues
```bash
# Reset migrations (last resort)
rm db_test.sqlite3
python manage.py migrate
```

### Permission Issues (Windows)
```powershell
# Use PowerShell for environment variables
$env:DJANGO_SETTINGS_MODULE = "job_tracker.settings.test"
```

## 📝 Development Tips

1. **Always use test environment** for UI debugging
2. **Reset frequently** to ensure clean state
3. **Use admin interface** to test model validation
4. **Check model constraints** in shell for complex scenarios
5. **Keep synthetic data realistic** but manageable in size

This setup enables rapid iteration without relying on incomplete UI flows while maintaining data integrity and business rule compliance.
