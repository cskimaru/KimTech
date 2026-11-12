import secrets
import string

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TimestampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


CATEGORY_CHOICES = [
    ("online", "Get online: domains, email, websites, memorials, backup, campaigns"),
    ("cloud", "Cloud & data protection consulting"),
]


class Service(TimestampedModel):
    """A consulting service line shown on the Services page (editable in admin)."""

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="cloud")
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
    """A vendor Nabec Networks Connection resells or partners with (e.g. Thales, eMudhra)."""

    STATUS_CHOICES = [
        ("planned", "Planned partnership — not yet formalized"),
        ("active", "Active, certified/contracted partner"),
    ]

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    icon = models.CharField(max_length=40, blank=True, help_text="Emoji or short label.")
    one_liner = models.CharField(max_length=200)
    about = models.TextField(help_text="A few sentences about the vendor.")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned",
        help_text=(
            "Only set 'active' once Nabec Networks Connection has an actual signed/certified "
            "relationship with this vendor. Until then this MUST stay 'planned' — the site "
            "explicitly labels planned partners as not yet formalized to avoid "
            "misrepresenting the relationship to visitors or to the vendor itself."
        ),
    )
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

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="cloud")
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
        ("domain_email", "Domain & business email"),
        ("website", "Website"),
        ("memorial", "Memorial website"),
        ("backup", "Cloud backup"),
        ("campaigns", "Email & SMS campaigns"),
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
    message = models.TextField(max_length=5000)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.get_service_interest_display()}"


def _new_reference():
    alphabet = string.ascii_uppercase.replace("O", "").replace("I", "") + "23456789"
    return "NB-" + "".join(secrets.choice(alphabet) for _ in range(6))


def _new_token():
    return secrets.token_urlsafe(24)


class Order(TimestampedModel):
    """A customer's order for domains, hosting, storage or a website, paid by M-Pesa.

    The customer sees it on a private page (unguessable token in the link), pays to the
    Till number with the order reference, and enters the M-Pesa confirmation code there.
    Nabec checks the payment, marks it paid and sets the services up.
    """

    SERVICE_CHOICES = [
        ("domain", "Domain name"),
        ("hosting", "Website hosting (cPanel)"),
        ("email", "Business email"),
        ("website", "Website design"),
        ("memorial", "Memorial website"),
        ("app_hosting", "App / cloud hosting (Python, Docker, VPS)"),
        ("storage", "Cloud storage & backup"),
        ("campaigns", "Email & SMS campaigns"),
    ]
    STATUS_CHOICES = [
        ("new", "New: awaiting payment"),
        ("payment_sent", "Payment code received: check M-Pesa"),
        ("paid", "Paid: set up services"),
        ("active", "Active: services delivered"),
        ("cancelled", "Cancelled"),
    ]

    reference = models.CharField(max_length=12, unique=True, default=_new_reference, editable=False)
    token = models.CharField(max_length=64, unique=True, default=_new_token, editable=False)
    package = models.ForeignKey(
        Package, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    services = models.CharField(max_length=200, help_text="Comma-separated service codes.")
    domain_name = models.CharField(max_length=253, blank=True)
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    company = models.CharField(max_length=150, blank=True)
    notes = models.TextField(max_length=3000, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new", db_index=True)
    mpesa_code = models.CharField(max_length=12, blank=True)
    amount_quoted = models.PositiveIntegerField(
        null=True, blank=True, help_text="KES. Fill in after confirming the order with the customer."
    )
    internal_notes = models.TextField(blank=True, help_text="Only visible in the admin.")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.reference} · {self.name}"

    def service_labels(self):
        labels = dict(self.SERVICE_CHOICES)
        return [labels.get(code, code) for code in self.services.split(",") if code]


class AffiliateLink(TimestampedModel):
    """An outgoing product link used in guides, served through /go/<slug>/.

    Guides always link to /go/<slug>/, never straight to the product. That way the real
    destination is set in one place: point it at the product's normal website at first,
    then paste in your personal affiliate link (and tick is_affiliate) once the program
    has approved you. Every guide that mentions the product starts earning at once.
    """

    name = models.CharField(max_length=120)
    slug = models.SlugField(
        max_length=60,
        unique=True,
        help_text="Used in guide text as /go/<slug>/, e.g. /go/semrush/.",
    )
    destination_url = models.URLField(
        max_length=500,
        help_text="Where visitors are sent. Your affiliate link once you have one, else the product's site.",
    )
    is_affiliate = models.BooleanField(
        default=False,
        help_text="Tick once destination_url is your own affiliate/referral link (we may earn a commission).",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Untick to stop the link working (visitors get a 404).",
    )
    clicks = models.PositiveIntegerField(default=0, editable=False)
    notes = models.TextField(
        blank=True,
        help_text="Private: program name, login/dashboard URL, commission terms, payout details.",
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("affiliate_redirect", kwargs={"slug": self.slug})


class Article(TimestampedModel):
    """A guide/blog post on the Guides page.

    The body uses a small, safe text format (see core/markup.py): blank lines separate
    paragraphs, "## " starts a heading, "- " starts a bullet, **bold**, and
    [link text](/go/semrush/) for links. Raw HTML is shown as text, never run.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.CharField(
        max_length=300, help_text="One or two sentences, shown on the Guides list and in search results."
    )
    body = models.TextField()
    published_at = models.DateField(help_text="Shown on the guide. Guides dated in the future stay hidden.")
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-published_at", "-id"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:220]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})
