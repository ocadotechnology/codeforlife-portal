from datetime import datetime, timedelta

import pytz
from common.models import Teacher, Student
from django.shortcuts import redirect
from django.urls import reverse_lazy


def old_login_form_redirect(request):
    return redirect(reverse_lazy("home"))


def has_user_lockout_expired(user: Teacher or Student) -> bool:
    return datetime.now(tz=pytz.utc) - user.blocked_time > timedelta(hours=24)
