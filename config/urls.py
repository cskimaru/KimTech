from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import RedirectView, TemplateView

from core.sitemaps import PartnerSitemap, StaticViewSitemap
from core import views

sitemaps = {"static": StaticViewSitemap, "partners": PartnerSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("partnerships/", views.partnerships, name="partnerships"),
    path("partnerships/<slug:slug>/", views.partner_detail, name="partner_detail"),
    path(
        "thales-partnership/",
        RedirectView.as_view(pattern_name="partner_detail", permanent=True, query_string=True),
        {"slug": "thales"},
    ),
    path("packages/", views.packages, name="packages"),
    path("contact/", views.contact, name="contact"),
    path("privacy-policy/", views.privacy_policy, name="privacy_policy"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),
]

handler404 = "core.views.handler404"
handler500 = "core.views.handler500"

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
