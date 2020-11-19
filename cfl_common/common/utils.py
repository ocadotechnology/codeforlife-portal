# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2020, Ocado Innovation Limited
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
