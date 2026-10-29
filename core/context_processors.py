from django.conf import settings


def company_info(request):
    return {
        "COMPANY_NAME": settings.COMPANY_NAME,
        "COMPANY_LOCATION": settings.COMPANY_LOCATION,
        "COMPANY_TAGLINE": settings.COMPANY_TAGLINE,
        "COMPANY_EMAIL": settings.COMPANY_EMAIL,
        "COMPANY_PHONES": settings.COMPANY_PHONES,
        "MPESA_TILL": settings.MPESA_TILL,
        "COMPANY_WHATSAPP_URL": f"https://wa.me/{settings.COMPANY_WHATSAPP}" if settings.COMPANY_WHATSAPP else "",
    }
