# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2021, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from __future__ import absolute_import

import functools
import time

from django.conf import settings
from django.core.cache import caches
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

cache_key = None


def get_cache_key():
    return cache_key


def is_ratelimited(
    request, group=None, fn=None, key=None, rate=None, method=ALL, increment=False
):
    usage = get_usage(request, group, fn, key, rate, method, increment)
    if usage is None:
        return False

    return usage["should_limit"]


def get_usage(
    request, group=None, fn=None, key=None, rate=None, method=ALL, increment=False
):
    global cache_key

    if group is None and fn is None:
        raise ImproperlyConfigured(
            "get_usage must be called with either " "`group` or `fn` arguments"
        )

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

    print(count)

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
