"""
Development settings for job_tracker project.
Extends base.py with development-specific configurations.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
# Uses separate database for development to avoid conflicts with test environment
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_dev.sqlite3',
    }
}

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Media files (for development only)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Disable CSRF protection for easier API testing in development
# WARNING: Only for development, never use in production!
# CSRF_COOKIE_SECURE = False
# CSRF_COOKIE_HTTPONLY = False
