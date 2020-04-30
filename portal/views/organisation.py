# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
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
import json

from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView

import portal.permissions as permissions
from portal import email_messages
from portal.forms.organisation import OrganisationJoinForm, OrganisationForm
from portal.helpers.emails import send_email, NOTIFICATION_EMAIL
from portal.models import School, Teacher, Class


class OrganisationFuzzyLookup(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (permissions.LoggedInAsTeacher,)

    def get(self, request):
        fuzzy_name = request.GET.get("fuzzy_name", None)
        school_data = []

        # The idea here is to return all schools that satisfy that each
        # part of the fuzzy_name (separated by spaces) occurs in either
        # school.name or school.postcode.
        # So it is an intersection of unions.

        if fuzzy_name and len(fuzzy_name) > 2:
            schools = School.objects.all()
            for part in fuzzy_name.split():
                schools = schools.filter(
                    Q(name__icontains=part) | Q(postcode__icontains=part)
                )

            self._search_schools(schools, school_data)

        return HttpResponse(json.dumps(school_data), content_type="application/json")

    def _search_schools(self, schools, school_data):
        for school in schools:
            admins = Teacher.objects.filter(school=school, is_admin=True)
            admin = admins.first()
            if admin:
                email = admin.new_user.email
                admin_domain = "*********" + email[email.find("@") :]
                school_data.append(
                    {
                        "id": school.id,
                        "name": school.name,
                        "postcode": school.postcode,
                        "admin_domain": admin_domain,
                    }
                )


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(
    permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login")
)
def organisation_create(request):

    teacher = request.user.new_teacher

    create_form = OrganisationForm(user=request.user)
    join_form = OrganisationJoinForm()

    if request.method == "POST":
        if "create_organisation" in request.POST:
            create_form = OrganisationForm(request.POST, user=request.user)
            if create_form.is_valid():
                data = create_form.cleaned_data
                name = data.get("name", "")
                postcode = data.get("postcode", "").upper()
                country = data.get("country", "")

                error, town, lat, lng = (
                    "",
                    "0",
                    "0",
                    "0",
                )  # lookup_coord(postcode, country)

                school = School.objects.create(
                    name=name,
                    postcode=postcode,
                    town=town,
                    latitude=lat,
                    longitude=lng,
                    country=country,
                )

                teacher.school = school
                teacher.is_admin = True
                teacher.save()

                messages.success(
                    request,
                    "The school or club '"
                    + teacher.school.name
                    + "' has been successfully added.",
                )

                return HttpResponseRedirect(reverse_lazy("onboarding-classes"))

        elif "join_organisation" in request.POST:
            process_join_form(
                request, teacher, OrganisationJoinForm, OrganisationJoinForm
            )

        else:
            return process_revoke_request(request, teacher)

    res = render(
        request,
        "portal/teach/onboarding_school.html",
        {"create_form": create_form, "join_form": join_form, "teacher": teacher},
    )

    return res


def compute_input_join_form(
    OrganisationJoinFormWithCaptcha, OrganisationJoinForm, using_captcha
):
    InputOrganisationJoinForm = (
        OrganisationJoinFormWithCaptcha if using_captcha else OrganisationJoinForm
    )
    return InputOrganisationJoinForm


def compute_output_join_form(
    OrganisationJoinFormWithCaptcha, OrganisationJoinForm, should_use_captcha
):
    OutputOrganisationJoinForm = (
        OrganisationJoinFormWithCaptcha if should_use_captcha else OrganisationJoinForm
    )
    return OutputOrganisationJoinForm


def send_pending_requests_emails(school, email_message):
    for admin in Teacher.objects.filter(school=school, is_admin=True):
        send_email(
            NOTIFICATION_EMAIL,
            [admin.new_user.email],
            email_message["subject"],
            email_message["message"],
        )


def process_join_form(
    request, teacher, InputOrganisationJoinForm, OutputOrganisationJoinForm
):
    join_form = InputOrganisationJoinForm(request.POST)
    if join_form.is_valid():
        school = get_object_or_404(School, id=join_form.cleaned_data["chosen_org"])

        teacher.pending_join_request = school
        teacher.save()

        email_message = email_messages.joinRequestPendingEmail(
            request, teacher.new_user.email
        )

        send_pending_requests_emails(school, email_message)

        email_message = email_messages.joinRequestSentEmail(request, school.name)
        send_email(
            NOTIFICATION_EMAIL,
            [teacher.new_user.email],
            email_message["subject"],
            email_message["message"],
        )

        messages.success(
            request,
            "Your request to join the school or club has been sent successfully.",
        )

        return render(
            request,
            "portal/teach/onboarding_school.html",
            {"school": school, "teacher": teacher},
        )

    else:
        join_form = OutputOrganisationJoinForm(request.POST)


def process_revoke_request(request, teacher):
    if "revoke_join_request" in request.POST:
        teacher.pending_join_request = None
        teacher.save()

        messages.success(
            request,
            "Your request to join the school or club has been revoked successfully.",
        )

        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(
    permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login")
)
def organisation_manage(request):
    return organisation_create(request)


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(
    permissions.logged_in_as_teacher, login_url=reverse_lazy("teacher_login")
)
def organisation_leave(request):
    teacher = request.user.new_teacher

    check_teacher_is_not_admin(teacher)

    if request.method == "POST":
        classes = Class.objects.filter(teacher=teacher)
        for klass in classes:
            teacher_id = request.POST.get(klass.access_code, None)
            if teacher_id:
                new_teacher = get_object_or_404(Teacher, id=teacher_id)
                klass.teacher = new_teacher
                klass.save()

        classes = Class.objects.filter(teacher=teacher)
        teachers = Teacher.objects.filter(school=teacher.school).exclude(id=teacher.id)

        if classes.exists():
            messages.info(
                request,
                "You still have classes, you must first move them to another teacher within your school or club.",
            )
            return render(
                request,
                "portal/teach/teacher_move_all_classes.html",
                {
                    "original_teacher": teacher,
                    "classes": classes,
                    "teachers": teachers,
                    "submit_button_text": "Move classes and leave",
                },
            )

        teacher.school = None
        teacher.save()

        messages.success(request, "You have successfully left the school or club.")

        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))


def check_teacher_is_not_admin(teacher):
    if teacher.is_admin:
        raise Http404
