"""Add the starter content that's new since 0003 (the Web Hosting and Domain Name packages).

Runs the same insert-if-missing seeding as 0003: rows that already exist, or were edited
in the admin, are left alone.
"""

import importlib

from django.db import migrations

seed = importlib.import_module("core.migrations.0003_seed_starter_content").seed


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_orders"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
