"""
Management command to create a default superuser for development/testing.
Idempotent - won't crash if user already exists.
Only runs in non-production environments.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.conf import settings
import os
import sys

User = get_user_model()


class Command(BaseCommand):
    help = 'Create default superuser for development/testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of superuser if it exists',
        )

    def handle(self, *args, **options):
        # Safety check - only run in dev/test environments
        if not (getattr(settings, 'DEBUG', False) and 
                ('test' in os.environ.get('DJANGO_SETTINGS_MODULE', '') or
                 'dev' in os.environ.get('DJANGO_SETTINGS_MODULE', '') or
                 'test' in sys.argv or
                 'dev' in sys.argv)):
            self.stdout.write(
                self.style.ERROR(
                    'This command can only be run in DEBUG mode with dev or test settings'
                )
            )
            return

        username = 'Brieuc'
        email = 'brieuc@example.com'
        password = 'password'

        try:
            user = User.objects.get(username=username)
            if options['force']:
                user.delete()
                self.stdout.write(f'Existing user "{username}" deleted.')
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Superuser "{username}" already exists.'
                    )
                )
                return
        except User.DoesNotExist:
            pass

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created superuser "{username}" with password "{password}"'
            )
        )
