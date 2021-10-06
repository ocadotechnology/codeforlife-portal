from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.cache import cache
from django.core.exceptions import FieldDoesNotExist
from two_factor.utils import default_device


def two_factor_cache_key(user):
    """Cache key for using_two_factor."""
    return "using-two-factor-%s" % user.pk


def _using_two_factor(user):
    """Returns whether the user is using 2fa or not."""
    return default_device(user)


def using_two_factor(user):
    """Returns whether the user is using 2fa or not (Cached)."""
    if hasattr(user, "using_two_factor_cache"):
        # First try local memory, as we call this a lot in one request
        return user.using_two_factor_cache
    cache_key = two_factor_cache_key(user)
    val = cache.get(cache_key)
    if val is not None:
        # If local memory failed, but we got it from memcache, set local memory
        user.using_two_factor_cache = val
        return val
    val = bool(_using_two_factor(user))

    # We didn't find it in the cache, so set it there and local memory
    cache.set(cache_key, val, None)  # Cache forever
    user.using_two_factor_cache = val
    return val


def field_exists(model, field):
    try:
        field = model._meta.get_field(field)
    except FieldDoesNotExist:
        return False
    return True


class LoginRequiredNoErrorMixin(LoginRequiredMixin):
    """
    Overwrites Django's 2.2 LoginRequiredMixin so as to not raise an error and
    redirect instead.
    """

    def handle_no_permission(self):
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name(),
        )
