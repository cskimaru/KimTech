from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import TemplateView

from core.sitemaps import StaticViewSitemap
from core import views

sitemaps = {"static": StaticViewSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("services/", views.services, name="services"),
    path("thales-partnership/", views.thales_partnership, name="thales_partnership"),
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
