import logging

from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import EngagementModel, Package, Service

logger = logging.getLogger(__name__)


def home(request):
    context = {
        "services": Service.objects.filter(is_published=True)[:4],
        "engagement_models": EngagementModel.objects.filter(is_published=True)[:3],
    }
    return render(request, "core/home.html", context)


def about(request):
    return render(request, "core/about.html")


def services(request):
    context = {"services": Service.objects.filter(is_published=True)}
    return render(request, "core/services.html", context)


def thales_partnership(request):
    context = {
        "engagement_models": EngagementModel.objects.filter(is_published=True),
    }
    return render(request, "core/thales_partnership.html", context)


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
