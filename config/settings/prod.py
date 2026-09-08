import dj_database_url

from .base import *  # noqa: F401,F403
from .base import env, BASE_DIR

DEBUG = False

if not ALLOWED_HOSTS:  # noqa: F405
    raise RuntimeError("ALLOWED_HOSTS must be set via the environment in production")

DATABASE_URL = env("DATABASE_URL", default="")
if DATABASE_URL:
    DATABASES = {  # noqa: F405
        "default": dj_database_url.parse(DATABASE_URL, conn_max_age=600, ssl_require=True)
    }

EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)

# --- Security hardening ---
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
