from django.conf import settings


def company_info(request):
    return {
        "COMPANY_NAME": settings.COMPANY_NAME,
        "COMPANY_LOCATION": settings.COMPANY_LOCATION,
        "COMPANY_TAGLINE": settings.COMPANY_TAGLINE,
        "COMPANY_EMAIL": settings.COMPANY_EMAIL,
        "COMPANY_PHONE": settings.COMPANY_PHONE,
    }
