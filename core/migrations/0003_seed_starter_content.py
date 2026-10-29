"""Insert the starter content (services, partners, packages...) on first deploy.

Reads core/fixtures/initial_content.json and creates any row that isn't there yet,
matching on primary key and, where the model has one, slug. Existing rows (including
anything edited in the admin) are never changed, so a fresh deploy shows a complete
site without a manual `loaddata`, and running `loaddata initial_content` later is
still safe.
"""

import json
from pathlib import Path

from django.core.exceptions import FieldDoesNotExist
from django.db import migrations

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "initial_content.json"


def seed(apps, schema_editor):
    created_models = set()
    for obj in json.loads(FIXTURE.read_text(encoding="utf-8")):
        Model = apps.get_model(obj["model"])
        if Model.objects.filter(pk=obj["pk"]).exists():
            continue
        fields = {}
        for name, value in obj["fields"].items():
            try:
                field = Model._meta.get_field(name)
            except FieldDoesNotExist:
                continue  # a field the historical model doesn't have yet
            fields[field.attname] = value  # foreign keys come as ids: partner -> partner_id
        if "slug" in fields and Model.objects.filter(slug=fields["slug"]).exists():
            continue
        Model.objects.create(pk=obj["pk"], **fields)
        created_models.add(Model)

    # Rows were inserted with explicit ids; move Postgres' id counters past them.
    connection = schema_editor.connection
    if created_models and connection.vendor == "postgresql":
        from django.core.management.color import no_style

        with connection.cursor() as cursor:
            for sql in connection.ops.sequence_reset_sql(no_style(), list(created_models)):
                cursor.execute(sql)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_categories_and_get_online_enquiries"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
