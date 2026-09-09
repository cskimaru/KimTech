from django.db import models
from django.urls import reverse
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


class Partner(TimestampedModel):
    """A vendor BEKA Ltd resells or partners with (e.g. Thales, eMudhra)."""

    STATUS_CHOICES = [
        ("active", "Active partner"),
        ("in_discussion", "Partnership in discussion"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon = models.CharField(max_length=40, blank=True, help_text="Emoji or short label.")
    one_liner = models.CharField(max_length=200)
    about = models.TextField(help_text="A few sentences about the vendor.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="in_discussion")
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("partner_detail", kwargs={"slug": self.slug})


class PartnerBenefit(TimestampedModel):
    """A 'why this fits SMEs'-style bullet point for a partner's detail page."""

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name="benefits")
    title = models.CharField(max_length=120)
    description = models.TextField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.partner.name}: {self.title}"


class EngagementModel(TimestampedModel):
    """One row of a partner's engagement-model table (VAR / MSP / Advisory, etc.)."""

    partner = models.ForeignKey(
        Partner, on_delete=models.CASCADE, related_name="engagement_models"
    )
    name = models.CharField(max_length=120)
    how_it_works = models.TextField()
    how_beka_monetizes = models.TextField()
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.partner.name}: {self.name}"


class Package(TimestampedModel):
    """A packaged SME offering, e.g. tiers of the Multi-Cloud Key Protection Package."""

    partner = models.ForeignKey(
        Partner, on_delete=models.SET_NULL, related_name="packages", null=True, blank=True
    )
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
        ("emudhra", "eMudhra Digital Signatures & PKI"),
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
