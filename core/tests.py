from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from .middleware import (
    ADMIN_LOGIN_MAX_ATTEMPTS,
    admin_login_throttle_key,
)
from .models import ContactMessage, EngagementModel, Package, Partner, Service


class PublicPagesTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nabec Networks Connection")

    def test_about_page_loads(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_services_page_lists_published_services_only(self):
        Service.objects.create(title="Visible Service", summary="x", is_published=True)
        Service.objects.create(title="Hidden Service", summary="x", is_published=False)
        response = self.client.get(reverse("services"))
        self.assertContains(response, "Visible Service")
        self.assertNotContains(response, "Hidden Service")

    def test_partnerships_hub_lists_published_partners_only(self):
        Partner.objects.create(name="Visible Partner", one_liner="x", about="x", is_published=True)
        Partner.objects.create(name="Hidden Partner", one_liner="x", about="x", is_published=False)
        response = self.client.get(reverse("partnerships"))
        self.assertContains(response, "Visible Partner")
        self.assertNotContains(response, "Hidden Partner")

    def test_partner_detail_page_loads(self):
        partner = Partner.objects.create(name="Test Partner", slug="test-partner", one_liner="x", about="x")
        EngagementModel.objects.create(
            partner=partner, name="Test Model", how_it_works="works", how_beka_monetizes="pays"
        )
        response = self.client.get(reverse("partner_detail", args=["test-partner"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Model")

    def test_unpublished_partner_detail_returns_404(self):
        Partner.objects.create(
            name="Hidden Partner", slug="hidden-partner", one_liner="x", about="x", is_published=False
        )
        response = self.client.get(reverse("partner_detail", args=["hidden-partner"]))
        self.assertEqual(response.status_code, 404)

    def test_old_thales_partnership_url_redirects(self):
        Partner.objects.create(name="Thales", slug="thales", one_liner="x", about="x")
        response = self.client.get("/thales-partnership/")
        self.assertRedirects(response, reverse("partner_detail", args=["thales"]), status_code=301)

    def test_packages_page_loads(self):
        Package.objects.create(
            name="Test Package", price_description="Free", features="One\nTwo"
        )
        response = self.client.get(reverse("packages"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Package")

    def test_privacy_policy_loads(self):
        response = self.client.get(reverse("privacy_policy"))
        self.assertEqual(response.status_code, 200)

    def test_sitemap_and_robots(self):
        self.assertEqual(
            self.client.get("/sitemap.xml").status_code, 200
        )
        self.assertEqual(self.client.get("/robots.txt").status_code, 200)

    def test_404_uses_custom_template(self):
        response = self.client.get("/this-page-does-not-exist/")
        self.assertEqual(response.status_code, 404)


class ContactFormTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_valid_submission_saves_and_redirects(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "company": "Example Co",
                "phone": "",
                "service_interest": "thales",
                "message": "We need help with DPoD.",
                "website": "",
            },
        )
        self.assertRedirects(response, reverse("contact"))
        self.assertEqual(ContactMessage.objects.count(), 1)
        saved = ContactMessage.objects.first()
        self.assertEqual(saved.email, "jane@example.com")

    def test_honeypot_field_rejects_bots(self):
        response = self.client.post(
            reverse("contact"),
            {
                "name": "Bot",
                "email": "bot@example.com",
                "message": "spam",
                "service_interest": "other",
                "website": "http://spam.example",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_missing_required_field_does_not_save(self):
        response = self.client.post(
            reverse("contact"),
            {"name": "", "email": "jane@example.com", "message": "Hi"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_notification_email_sent_when_configured(self):
        with self.settings(CONTACT_NOTIFY_EMAIL="ops@beka.co.ke"):
            self.client.post(
                reverse("contact"),
                {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                    "message": "Need a quote.",
                    "service_interest": "cloud",
                    "website": "",
                },
            )
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("ops@beka.co.ke", mail.outbox[0].to)


class ContactFormRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def _post(self):
        return self.client.post(
            reverse("contact"),
            {
                "name": "Jane Doe",
                "email": "jane@example.com",
                "message": "Hello there, this is a test message.",
                "service_interest": "other",
                "website": "",
            },
        )

    def test_excess_submissions_from_same_ip_are_blocked(self):
        from .views import CONTACT_RATE_LIMIT_MAX_ATTEMPTS

        for _ in range(CONTACT_RATE_LIMIT_MAX_ATTEMPTS):
            response = self._post()
            self.assertRedirects(response, reverse("contact"))

        blocked_count_before = ContactMessage.objects.count()
        response = self._post()
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "too many times")
        self.assertEqual(ContactMessage.objects.count(), blocked_count_before)


class AdminLoginThrottleTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_admin_login_blocked_after_too_many_failures(self):
        login_url = reverse("admin:login")
        for _ in range(ADMIN_LOGIN_MAX_ATTEMPTS):
            self.client.post(login_url, {"username": "nope", "password": "wrong"})

        key = admin_login_throttle_key("127.0.0.1")
        self.assertGreaterEqual(cache.get(key, 0), ADMIN_LOGIN_MAX_ATTEMPTS)

        response = self.client.post(login_url, {"username": "nope", "password": "wrong"})
        self.assertEqual(response.status_code, 429)


class SecurityHeadersTests(TestCase):
    def test_public_page_has_strict_csp(self):
        response = self.client.get(reverse("home"))
        self.assertIn("Content-Security-Policy", response.headers)
        self.assertIn("default-src 'self'", response.headers["Content-Security-Policy"])
        self.assertIn("Permissions-Policy", response.headers)

    def test_admin_page_is_not_forced_into_site_csp(self):
        response = self.client.get(reverse("admin:login"))
        self.assertNotIn("Content-Security-Policy", response.headers)
