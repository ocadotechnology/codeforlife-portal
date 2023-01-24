from __future__ import absolute_import

import datetime
import pytz
import re


from common.models import Teacher, Student
from django.contrib.auth import logout
from django.shortcuts import render
from functools import wraps
from ratelimit import ALL, UNSAFE

from portal.helpers.ratelimit import is_ratelimited
from portal.templatetags.app_tags import is_logged_in

__all__ = ["ratelimit"]


def ratelimit(group=None, key=None, rate=None, method=ALL, block=False, is_teacher=True):
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

                user_lockout = None

                lockout_template = "portal/locked_out.html"

                if request.user.is_anonymous:
                    data = request.POST
                    if is_teacher:
                        username = data.get("auth-username")
                    else:
                        username = data.get("username")

                    access_code_re = re.search("/login/student/(\w+)", request.get_full_path())
                    model_finder = model.objects.filter
                    # look for school student
                    # if access code not found (AttributeError)
                    # if student not found (IndexError)
                    # move on to another try block
                    # similar logic followed afterwards
                    try:
                        user_lockout = model_finder(
                            new_user__first_name=username,
                            class_field__access_code=access_code_re.group(1),  # extract the found text from regex
                        )[0]
                        lockout_template = "portal/locked_out_school_student.html"
                    except (AttributeError, IndexError):
                        pass
                    # look for indy student or teacher
                    try:
                        user_lockout = model_finder(new_user__username=username)[0]
                    except IndexError:
                        pass
                else:
                    user_lockout = model.objects.get(new_user=request.user)
                if user_lockout:
                    user_lockout.blocked_time = datetime.datetime.now(tz=pytz.utc)
                    user_lockout.save()

                    if is_logged_in(request.user):
                        logout(request)

                    return render(
                        request,
                        lockout_template,
                        {"is_teacher": is_teacher},
                    )

            return fn(request, *args, **kw)

        return _wrapped

    return decorator


ratelimit.ALL = ALL
ratelimit.UNSAFE = UNSAFE
