from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from django.utils import timezone

from .models import Article, Partner


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
            "order",
            "articles",
            "affiliate_disclosure",
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


class ArticleSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Article.objects.filter(is_published=True, published_at__lte=timezone.localdate())

    def lastmod(self, article):
        return article.updated_at
