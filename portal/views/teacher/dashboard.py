# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
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
from functools import partial
import json
from recaptcha import RecaptchaClient

from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal import app_settings, emailMessages
from portal.models import School, Teacher, Class
from portal.forms.organisation import OrganisationJoinForm, OrganisationForm
from portal.permissions import logged_in_as_teacher
from portal.helpers.emails import send_email, NOTIFICATION_EMAIL
from portal.helpers.location import lookup_coord

from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(app_settings.RECAPTCHA_PRIVATE_KEY, app_settings.RECAPTCHA_PUBLIC_KEY)


@login_required(login_url=reverse_lazy('login_new'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('login_new'))
def dashboard_teacher_view(request, is_admin):
    teacher = request.user.new_teacher
    school = teacher.school
    classes = Class.objects.filter(teacher=teacher)

    coworkers = Teacher.objects.filter(school=school).order_by('new_user__last_name', 'new_user__first_name')

    join_requests = Teacher.objects.filter(pending_join_request=school).order_by('new_user__last_name', 'new_user__first_name')

    return render(request, 'redesign/teach_new/dashboard.html', {
        'teacher': teacher,
        'classes': classes,
        'is_admin': is_admin,
        'coworkers': coworkers,
        'join_requests': join_requests,
    })


@login_required(login_url=reverse_lazy('login_new'))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy('login_new'))
def dashboard_manage(request):
    teacher = request.user.new_teacher

    if teacher.school:
        return dashboard_teacher_view(request, teacher.is_admin)
