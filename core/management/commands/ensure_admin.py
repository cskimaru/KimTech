"""Create the first admin account from environment variables, once.

For hosts without a shell (such as Render's free plan). Set DJANGO_SUPERUSER_USERNAME,
DJANGO_SUPERUSER_EMAIL and DJANGO_SUPERUSER_PASSWORD, deploy, sign in at /admin/, then
delete DJANGO_SUPERUSER_PASSWORD from the host's settings. Does nothing when the
variables aren't set or when any superuser already exists, so it never changes an
existing account or password.
"""

import os

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create the first superuser from DJANGO_SUPERUSER_* environment variables, if none exists."

    def handle(self, *args, **options):
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "")
        User = get_user_model()

        if not (username and password):
            return
        if User.objects.filter(is_superuser=True).exists():
            self.stdout.write("An admin account already exists; nothing to do.")
            return
        try:
            validate_password(password, User(username=username, email=email))
        except ValidationError as e:
            self.stderr.write("Admin account not created: " + " ".join(e.messages))
            return
        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(f"Created admin account '{username}'. Now remove DJANGO_SUPERUSER_PASSWORD from the settings.")
