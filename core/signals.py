from django.contrib.auth.signals import user_login_failed
from django.core.cache import cache
from django.dispatch import receiver

from .middleware import (
    ADMIN_LOGIN_WINDOW_SECONDS,
    admin_login_throttle_key,
    get_client_ip,
)


@receiver(user_login_failed)
def record_failed_login(sender, credentials, request=None, **kwargs):
    if request is None:
        return
    key = admin_login_throttle_key(get_client_ip(request))
    attempts = cache.get(key, 0) + 1
    cache.set(key, attempts, timeout=ADMIN_LOGIN_WINDOW_SECONDS)
