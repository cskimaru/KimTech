from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return [
            "home",
            "about",
            "services",
            "thales_partnership",
            "packages",
            "contact",
            "privacy_policy",
        ]

    def location(self, item):
        return reverse(item)
