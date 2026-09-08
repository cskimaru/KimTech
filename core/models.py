from django.db import models
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Service(TimestampedModel):
    """A consulting service line shown on the Services page (editable in admin)."""

    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon = models.CharField(
        max_length=40,
        blank=True,
        help_text="A short label/emoji used as the card icon, e.g. 'cloud'.",
    )
    summary = models.CharField(max_length=280)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class EngagementModel(TimestampedModel):
    """One row of the Thales partnership engagement-model table."""

    name = models.CharField(max_length=120)
    how_it_works = models.TextField()
    how_beka_monetizes = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name


class Package(TimestampedModel):
    """A packaged SME offering, e.g. tiers of the Multi-Cloud Key Protection Package."""

    name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=200, blank=True)
    price_description = models.CharField(
        max_length=120,
        blank=True,
        help_text="e.g. 'From KES 150,000/month' or 'Custom quote'.",
    )
    features = models.TextField(help_text="One feature per line.")
    is_featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def feature_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]


class ContactMessage(TimestampedModel):
    SERVICE_CHOICES = [
        ("cloud", "Cloud & Multi-Cloud Consulting"),
        ("thales", "Thales Data Protection (DPoD / CipherTrust)"),
        ("managed", "Managed Security Services"),
        ("advisory", "Security & Compliance Advisory"),
        ("other", "Other / Not sure yet"),
    ]

    name = models.CharField(max_length=120)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=40, blank=True)
    service_interest = models.CharField(
        max_length=20, choices=SERVICE_CHOICES, default="other"
    )
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.get_service_interest_display()}"
