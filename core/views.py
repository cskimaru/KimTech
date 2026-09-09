import logging

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ContactForm
from .models import Package, Partner, Service

logger = logging.getLogger(__name__)


def home(request):
    context = {
        "services": Service.objects.filter(is_published=True)[:4],
        "partners": Partner.objects.filter(is_published=True),
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def services(request):
    context = {"services": Service.objects.filter(is_published=True)}
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
    context = {"packages": Package.objects.filter(is_published=True)}
    return render(request, "core/packages.html", context)


def contact(request):
    if request.method == "POST":
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
                "Thanks for reaching out — a member of the BEKA Ltd team will "
                "get back to you within one business day.",
            )
            return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "core/contact.html", {"form": form})


def privacy_policy(request):
    return render(request, "core/privacy.html")


def handler404(request, exception=None):
    return render(request, "404.html", status=404)


def handler500(request):
    return render(request, "500.html", status=500)
