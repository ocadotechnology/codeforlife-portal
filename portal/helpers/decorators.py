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
