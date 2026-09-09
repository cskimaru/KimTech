from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Partner


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return [
            "home",
            "about",
            "services",
            "partnerships",
            "packages",
            "contact",
            "privacy_policy",
        ]

    def location(self, item):
        return reverse(item)


class PartnerSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Partner.objects.filter(is_published=True)

    def location(self, partner):
        return partner.get_absolute_url()

    def lastmod(self, partner):
        return partner.updated_at
