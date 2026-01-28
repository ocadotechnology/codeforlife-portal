from datetime import datetime, timedelta

from common.models import Teacher, Student
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.timezone import make_aware


def old_login_form_redirect(request):
    return redirect(reverse_lazy("home"))


def has_user_lockout_expired(user: Teacher or Student) -> bool:
    return make_aware(datetime.now()) - user.blocked_time > timedelta(hours=24)
