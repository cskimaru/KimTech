from django.core import mail
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage, EngagementModel, Package, Service


class PublicPagesTests(TestCase):
    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "BEKA Ltd")

    def test_about_page_loads(self):
        response = self.client.get(reverse("about"))
        self.assertEqual(response.status_code, 200)

    def test_services_page_lists_published_services_only(self):
        Service.objects.create(title="Visible Service", summary="x", is_published=True)
        Service.objects.create(title="Hidden Service", summary="x", is_published=False)
        response = self.client.get(reverse("services"))
        self.assertContains(response, "Visible Service")
        self.assertNotContains(response, "Hidden Service")

    def test_thales_partnership_page_loads(self):
        EngagementModel.objects.create(
            name="Test Model", how_it_works="works", how_beka_monetizes="pays"
        )
        response = self.client.get(reverse("thales_partnership"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Model")

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
