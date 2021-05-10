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

import datetime
import pytz
from functools import wraps

from common.models import Teacher, Student
from django.contrib.auth import logout
from django.shortcuts import render
from ratelimit import ALL, UNSAFE

from portal.helpers.ratelimit import is_ratelimited
from portal.templatetags.app_tags import is_logged_in

__all__ = ["ratelimit"]


def ratelimit(
    group=None, key=None, rate=None, method=ALL, block=False, is_teacher=True
):
    """
    Ratelimit decorator, adding custom functionality to django-ratelimit's default
    decorator. On block, the user is logged out, redirected to the "locked out" page,
    and passes in whether the user is a teacher or not, depending on the is_teacher
    argument. The user is blocked and the time at which they are blocked is saved.
    """

    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kw):
            old_limited = getattr(request, "limited", False)
            ratelimited = is_ratelimited(
                request=request,
                group=group,
                fn=fn,
                key=key,
                rate=rate,
                method=method,
                increment=True,
            )
            request.limited = ratelimited or old_limited

            if ratelimited and block:
                if is_teacher:
                    model = Teacher
                else:
                    model = Student

                user = None

                if request.user.is_anonymous:
                    data = request.POST
                    if is_teacher:
                        username = data.get("auth-username")
                    else:
                        username = data.get("username")

                    if model.objects.filter(new_user__username=username).exists():
                        user = model.objects.get(new_user__username=username)
                else:
                    user = model.objects.get(new_user=request.user)

                if user:
                    user.blocked_time = datetime.datetime.now(tz=pytz.utc)
                    user.save()

                    if is_logged_in(request.user):
                        logout(request)

                    return render(
                        request,
                        "portal/locked_out.html",
                        {"is_teacher": is_teacher},
                    )

            return fn(request, *args, **kw)

        return _wrapped

    return decorator


ratelimit.ALL = ALL
ratelimit.UNSAFE = UNSAFE
