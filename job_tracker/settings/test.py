"""
Test settings for job_tracker project.
Extends base.py with test-specific configurations.
Isolated database and settings for safe testing.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Dedicated test database - completely isolated from dev/production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# Email backend for testing (suppresses emails)
EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

# Disable migrations for faster test runs
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# Uncomment the following line to disable migrations during testing
# MIGRATION_MODULES = DisableMigrations()

# Password hashing for faster tests (less secure, only for testing!)
# PASSWORD_HASHERS = [
#     'django.contrib.auth.hashers.MD5PasswordHasher',
# ]

# Simplified logging for tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
}
