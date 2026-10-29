from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.urls import NoReverseMatch, reverse

ADMIN_LOGIN_MAX_ATTEMPTS = 10
ADMIN_LOGIN_WINDOW_SECONDS = 15 * 60


def admin_login_throttle_key(ip_address):
    return f"admin-login-failures:{ip_address}"


def get_client_ip(request):
    forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


class SecurityHeadersMiddleware:
    """Adds a strict Content-Security-Policy and Permissions-Policy to
    public pages. The admin is exempted: it is authenticated-only and
    Django's own admin assets aren't guaranteed to satisfy a strict CSP.
    """

    CSP = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self'; "
        "img-src 'self' data:; "
        "font-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    PERMISSIONS_POLICY = (
        "camera=(), microphone=(), geolocation=(), payment=(), usb=()"
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        admin_prefix = f"/{settings.ADMIN_URL}/"
        if not request.path.startswith(admin_prefix):
            response.setdefault("Content-Security-Policy", self.CSP)
            response.setdefault("Permissions-Policy", self.PERMISSIONS_POLICY)
        return response


class AdminLoginThrottleMiddleware:
    """Blocks further admin login attempts from an IP after too many
    failures in a short window. Pairs with the `user_login_failed` signal
    receiver in core.signals, which increments the counter.

    This uses Django's default cache (in-process LocMemCache), which is
    correct for the current single-worker, single-instance deployment.
    If this app is ever scaled to multiple workers/instances, switch to a
    shared cache backend (e.g. Redis) or this throttle becomes per-process
    and much weaker.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_login_path = None

    def __call__(self, request):
        if self.admin_login_path is None:
            try:
                self.admin_login_path = reverse("admin:login")
            except NoReverseMatch:
                self.admin_login_path = f"/{settings.ADMIN_URL}/login/"

        if request.method == "POST" and request.path == self.admin_login_path:
            ip_address = get_client_ip(request)
            attempts = cache.get(admin_login_throttle_key(ip_address), 0)
            if attempts >= ADMIN_LOGIN_MAX_ATTEMPTS:
                return HttpResponse(
                    "Too many failed login attempts. Please try again later.",
                    status=429,
                    content_type="text/plain",
                )

        return self.get_response(request)


class CanonicalHostMiddleware:
    """Sends visitors who arrive on another host name (e.g. the Render onrender.com
    address, or www) to CANONICAL_HOST, keeping the path, so search engines and
    shared links only ever use the real domain. Does nothing when CANONICAL_HOST
    is unset (development and tests)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        canonical = getattr(settings, "CANONICAL_HOST", "")
        if canonical and request.get_host().split(":")[0].lower() != canonical:
            return HttpResponsePermanentRedirect(f"https://{canonical}{request.get_full_path()}")
        return self.get_response(request)
