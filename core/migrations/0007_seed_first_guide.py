"""Add the first guide and the affiliate links it uses (insert-if-missing).

Rows that already exist, or were edited in the admin, are never changed. The Semrush
link starts out pointing at Semrush's normal website; replace it with your own
affiliate link in the admin (Affiliate links > Semrush) once you've been approved.
"""

import datetime
from pathlib import Path

from django.db import migrations

BODY = Path(__file__).resolve().parent.parent / "content" / "seo-for-kenyan-small-businesses.txt"

LINKS = [
    {
        "slug": "semrush",
        "name": "Semrush",
        "destination_url": "https://www.semrush.com/",
        "notes": (
            "Not an affiliate link yet. Join the Semrush affiliate program (via Impact), then paste "
            "your affiliate link into Destination URL and tick 'Is affiliate'."
        ),
    },
]


def seed(apps, schema_editor):
    AffiliateLink = apps.get_model("core", "AffiliateLink")
    Article = apps.get_model("core", "Article")
    for link in LINKS:
        if not AffiliateLink.objects.filter(slug=link["slug"]).exists():
            AffiliateLink.objects.create(**link)
    slug = "seo-for-kenyan-small-businesses"
    if not Article.objects.filter(slug=slug).exists():
        Article.objects.create(
            slug=slug,
            title="SEO for Kenyan small businesses: start free, then decide if Semrush is worth it",
            summary=(
                "How to show up on Google and Google Maps using free tools, and when a paid "
                "SEO tool like Semrush starts to pay for itself."
            ),
            body=BODY.read_text(encoding="utf-8"),
            published_at=datetime.date(2026, 11, 12),
            is_published=True,
        )


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_affiliatelink_article"),
    ]

    operations = [
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
