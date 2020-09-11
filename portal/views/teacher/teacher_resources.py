# -*- coding: utf-8 -*-

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render

from common.permissions import logged_in_as_teacher
from portal.strings.teacher_resources import RESOURCES_BANNER


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def teacher_resources(request):
    return render(
        request, "portal/teach/teacher_resources.html", {"BANNER": RESOURCES_BANNER}
    )
