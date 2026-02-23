"""
Test minimal pour vérifier que Django démarre correctement.
Ce test assure que la configuration de base fonctionne.
"""

from django.test import TestCase
from django.conf import settings
from django.test.client import Client


class DjangoStartupTest(TestCase):
    """Test basique pour vérifier que Django fonctionne."""

    def test_django_settings_loaded(self):
        """Vérifie que les settings Django sont correctement chargés."""
        self.assertTrue(hasattr(settings, "DEBUG"))
        self.assertTrue(hasattr(settings, "DATABASES"))
        self.assertEqual(
            settings.DATABASES["default"]["ENGINE"], "django.db.backends.sqlite3"
        )

    def test_django_client_can_initialize(self):
        """Vérifie que le client Django peut s'initialiser."""

        client = Client()
        self.assertIsNotNone(client)

    def test_apps_configured(self):
        """Vérifie que les applications Django sont configurées."""
        self.assertTrue(hasattr(settings, "INSTALLED_APPS"))
        self.assertIn("django.contrib.admin", settings.INSTALLED_APPS)
        self.assertIn("candidatures", settings.INSTALLED_APPS)
