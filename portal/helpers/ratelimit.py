"""
This file is a customisation of the django-ratelimit library. The purpose of this
customisation is to give us the ability to access and the delete the cache key
associated with the ratelimit counter. We want this so that we can reset the
ratelimit counter whenever a successful request is performed on any ratelimited
view.

is_ratelimited() and get_usage() are the same as in django-ratelimit, with the
exception of the line `global cache_key` at the start of get_usage().
is_ratelimited() is called in the customised django-ratelimit ratelimit
decorator found in portal/helpers/decorators.py.

`get_ratelimit_cache_key_for_user`, `get_ratelimit_count_for_user`
and `clear_ratelimit_cache_for_user` are custom functions.

More info on the core methods of django-ratelimit can be found here:
https://django-ratelimit.readthedocs.io/en/stable/usage.html#core-methods
"""
from __future__ import absolute_import

import functools
import time

from django.conf import settings
from django.core.cache import caches, cache
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string
from ratelimit import ALL, UNSAFE
from ratelimit.core import (
    _split_rate,
    _method_match,
    _ACCESSOR_KEYS,
    _SIMPLE_KEYS,
    _get_window,
    EXPIRATION_FUDGE,
    _make_cache_key,
)

from portal.helpers.regexes import EMAIL_REGEX_PATTERN
from portal.helpers.request_handlers import get_access_code_from_request

RATELIMIT_LOGIN_GROUP = "login"
RATELIMIT_LOGIN_RATE = "5/d"
RATELIMIT_LOGIN_RATE_SCHOOL_STUDENT = "10/d"
RATELIMIT_METHOD = "POST"

RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_GROUP = "user_already_registered_email"
RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_RATE = "1/d"


def school_student_key(group, request):
    access_code = get_access_code_from_request(request)
    return f'{request.POST.get("username", "")},{access_code}'


def get_ratelimit_cache_key_for_user(user: str):
    # check for email quickly

    user_rate = RATELIMIT_LOGIN_RATE if EMAIL_REGEX_PATTERN.match(user) else RATELIMIT_LOGIN_RATE_SCHOOL_STUDENT
    _, period = _split_rate(rate=user_rate)
    window = _get_window(value=user, period=period)
    cache_key = _make_cache_key(
        group=RATELIMIT_LOGIN_GROUP,
        window=window,
        rate=user_rate,
        value=user,
        methods=RATELIMIT_METHOD,
    )
    return cache_key


def get_ratelimit_count_for_user(user: str):
    cache_key = get_ratelimit_cache_key_for_user(user)
    return cache.get(cache_key)


def clear_ratelimit_cache_for_user(user: str):
    cache_key = get_ratelimit_cache_key_for_user(user)
    cache.delete(cache_key)


def is_ratelimited(request, group=None, fn=None, key=None, rate=None, method=ALL, increment=False):
    """
    As in django-ratelimit. Calls "get_usage" defined below to enable the usage of
    the custom cache_key functionality.
    """
    usage = get_usage(request, group, fn, key, rate, method, increment)
    if usage is None:
        return False

    return usage["should_limit"]


def get_usage(request, group=None, fn=None, key=None, rate=None, method=ALL, increment=False):
    """
    As in django-ratelimit. Makes cache_key global so it can be called outside the scope
    and the cache can be accessed at later times.
    """
    global cache_key

    if group is None and fn is None:
        raise ImproperlyConfigured("get_usage must be called with either " "`group` or `fn` arguments")

    if not getattr(settings, "RATELIMIT_ENABLE", True):
        return None

    if not _method_match(request, method):
        return None

    if group is None:
        parts = []

        if isinstance(fn, functools.partial):
            fn = fn.func

        # Django <2.1 doesn't use a partial. This is ugly and inelegant, but
        # throwing __qualname__ into the list below helps.
        if fn.__name__ == "bound_func":
            fn = fn.__closure__[0].cell_contents

        if hasattr(fn, "__module__"):
            parts.append(fn.__module__)

        if hasattr(fn, "__self__"):
            parts.append(fn.__self__.__class__.__name__)

        parts.append(fn.__qualname__)
        group = ".".join(parts)

    if callable(rate):
        rate = rate(group, request)
    elif isinstance(rate, str) and "." in rate:
        ratefn = import_string(rate)
        rate = ratefn(group, request)

    if rate is None:
        return None
    limit, period = _split_rate(rate)
    if period <= 0:
        raise ImproperlyConfigured("Ratelimit period must be greater than 0")

    if not key:
        raise ImproperlyConfigured("Ratelimit key must be specified")
    if callable(key):
        value = key(group, request)
    elif key in _SIMPLE_KEYS:
        value = _SIMPLE_KEYS[key](request)
    elif ":" in key:
        accessor, k = key.split(":", 1)
        if accessor not in _ACCESSOR_KEYS:
            raise ImproperlyConfigured("Unknown ratelimit key: %s" % key)
        value = _ACCESSOR_KEYS[accessor](request, k)
    elif "." in key:
        keyfn = import_string(key)
        value = keyfn(group, request)
    else:
        raise ImproperlyConfigured("Could not understand ratelimit key: %s" % key)

    window = _get_window(value, period)
    initial_value = 1 if increment else 0

    cache_name = getattr(settings, "RATELIMIT_USE_CACHE", "default")
    cache = caches[cache_name]

    if value == "":
        return {
            "count": 0,
            "limit": 0,
            "should_limit": False,
            "time_left": -1,
        }
    else:
        cache_key = _make_cache_key(group, window, rate, value, method)

    count = None
    added = cache.add(cache_key, initial_value, period + EXPIRATION_FUDGE)
    if added:
        count = initial_value
    else:
        if increment:
            try:
                # python3-memcached will throw a ValueError if the server is
                # unavailable or (somehow) the key doesn't exist. redis, on the
                # other hand, simply returns None.
                count = cache.incr(cache_key)
            except ValueError:
                pass
        else:
            count = cache.get(cache_key, initial_value)

    # Getting or setting the count from the cache failed
    if count is None:
        if getattr(settings, "RATELIMIT_FAIL_OPEN", False):
            return None
        return {
            "count": 0,
            "limit": 0,
            "should_limit": True,
            "time_left": -1,
        }

    time_left = window - int(time.time())
    return {
        "count": count,
        "limit": limit,
        "should_limit": count > limit,
        "time_left": time_left,
    }


is_ratelimited.ALL = ALL
is_ratelimited.UNSAFE = UNSAFE
get_usage.ALL = ALL
get_usage.UNSAFE = UNSAFE
