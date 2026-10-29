import logging

from django.contrib import messages
from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .middleware import get_client_ip
from .models import ContactMessage, Package, Partner, Service

logger = logging.getLogger(__name__)

CONTACT_RATE_LIMIT_MAX_ATTEMPTS = 10
CONTACT_RATE_LIMIT_WINDOW_SECONDS = 10 * 60


def home(request):
    published = Service.objects.filter(is_published=True)
    context = {
        "online_services": published.filter(category="online"),
        "services": published.filter(category="cloud")[:4],
        "partners": Partner.objects.filter(is_published=True),
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def services(request):
    published = Service.objects.filter(is_published=True)
    context = {
        "online_services": published.filter(category="online"),
        "services": published.filter(category="cloud"),
    }
    return render(request, "core/services.html", context)


def partnerships(request):
    context = {"partners": Partner.objects.filter(is_published=True)}
    return render(request, "core/partnerships.html", context)


def partner_detail(request, slug):
    partner = get_object_or_404(Partner, slug=slug, is_published=True)
    context = {
        "partner": partner,
        "benefits": partner.benefits.all(),
        "engagement_models": partner.engagement_models.filter(is_published=True),
        "packages": partner.packages.filter(is_published=True),
    }
    return render(request, "core/partner_detail.html", context)


def packages(request):
    published = Package.objects.filter(is_published=True)
    context = {
        "online_packages": published.filter(category="online"),
        "packages": published.filter(category="cloud"),
    }
    return render(request, "core/packages.html", context)


def contact(request):
    if request.method == "POST":
        rate_limit_key = f"contact-submissions:{get_client_ip(request)}"
        attempts = cache.get(rate_limit_key, 0)
        if attempts >= CONTACT_RATE_LIMIT_MAX_ATTEMPTS:
            messages.error(
                request,
                "You've submitted this form too many times recently. "
                "Please wait a few minutes and try again.",
            )
            return render(request, "core/contact.html", {"form": ContactForm()})
        cache.set(rate_limit_key, attempts + 1, timeout=CONTACT_RATE_LIMIT_WINDOW_SECONDS)

        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()

            notify_to = getattr(settings, "CONTACT_NOTIFY_EMAIL", "")
            if notify_to:
                try:
                    send_mail(
                        subject=f"New enquiry: {contact_message.get_service_interest_display()}",
                        message=(
                            f"Name: {contact_message.name}\n"
                            f"Email: {contact_message.email}\n"
                            f"Company: {contact_message.company}\n"
                            f"Phone: {contact_message.phone}\n\n"
                            f"{contact_message.message}"
                        ),
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[notify_to],
                        fail_silently=True,
                    )
                except Exception:
                    logger.exception("Failed to send contact-form notification email")

            messages.success(
                request,
                f"Thanks for reaching out — a member of the {settings.COMPANY_NAME} team "
                "will get back to you within one business day.",
            )
            return redirect("contact")
    else:
        # Links such as /contact/?service=memorial arrive with that service already chosen.
        choices = dict(ContactMessage.SERVICE_CHOICES)
        service = request.GET.get("service", "")
        form = ContactForm(initial={"service_interest": service} if service in choices else None)

    return render(request, "core/contact.html", {"form": form})


def privacy_policy(request):
    return render(request, "core/privacy.html")


def handler404(request, exception=None):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)
