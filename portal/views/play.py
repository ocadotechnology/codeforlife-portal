# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
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

from django.contrib import messages as messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render
from django.views.generic.edit import FormView

from portal import email_messages
from portal.forms.play import (
    StudentEditAccountForm,
    StudentJoinOrganisationForm,
    IndependentStudentEditAccountForm,
)
from portal.helpers.emails import (
    send_email,
    send_verification_email,
    NOTIFICATION_EMAIL,
)
from portal.models import Student
from portal.permissions import logged_in_as_student
from ratelimit.decorators import ratelimit


@login_required(login_url=reverse_lazy("login_view"))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy("login_view"))
def student_details(request):
    return render(request, "portal/play/student_details.html")


def get_form(self, form_class):
    user = self.request.user
    if form_class is None:
        form_class = self.get_form_class()
    return form_class(user, **self.get_form_kwargs())


def process_form(self, process_function, form, view):
    student = self.request.user.new_student
    process_function(form, student, self.request)
    return super(view, self).form_valid(form)


class SchoolStudentEditAccountView(FormView):
    form_class = StudentEditAccountForm
    template_name = "../templates/portal/play/student_edit_account.html"
    success_url = reverse_lazy("student_details")
    model = Student

    def form_valid(self, form):
        return process_form(
            self,
            self.process_student_edit_account_form,
            form,
            SchoolStudentEditAccountView,
        )

    def process_student_edit_account_form(self, form, student, request):
        data = form.cleaned_data
        # check not default value for CharField
        if data["password"] != "":
            student.new_user.set_password(data["password"])
            student.new_user.save()
            update_session_auth_hash(request, form.user)

        messages.success(
            request, "Your account details have been changed successfully."
        )

    def get_form(self, form_class=None):
        return get_form(self, form_class)


class IndependentStudentEditAccountView(FormView):
    form_class = IndependentStudentEditAccountForm
    template_name = "../templates/portal/play/student_edit_account.html"
    model = Student
    initial = {"name": "Could not find name"}
    changing_email = False

    def get_form_kwargs(self):
        kwargs = super(IndependentStudentEditAccountView, self).get_form_kwargs()
        kwargs["initial"]["name"] = "{}{}".format(
            self.request.user.first_name, self.request.user.last_name
        )
        return kwargs

    def get_form(self, form_class=None):
        return get_form(self, form_class)

    def get_success_url(self):
        if self.changing_email:
            return reverse_lazy("email_verification")
        else:
            return reverse_lazy("student_details")

    def form_valid(self, form):
        return process_form(
            self,
            self.process_independent_student_edit_account_form,
            form,
            IndependentStudentEditAccountView,
        )

    def process_independent_student_edit_account_form(self, form, student, request):
        data = form.cleaned_data

        # check not default value for CharField
        self.check_update_password(form, student, request, data)

        # allow individual students to update more
        self.changing_email, new_email = self.update_email(student, request, data)

        self.update_name(student, data)

        messages.success(
            request, "Your account details have been changed successfully."
        )

        if self.changing_email:
            logout(request)

    def check_update_password(self, form, student, request, data):
        if data["password"] != "":
            student.new_user.set_password(data["password"])
            student.new_user.save()
            update_session_auth_hash(request, form.user)

    def update_email(self, student, request, data):
        changing_email = False
        new_email = data["email"]
        if new_email != "" and new_email != student.new_user.email:
            # new email to set and verify
            changing_email = True
            send_verification_email(request, student.new_user, new_email)
        return changing_email, new_email

    def update_name(self, student, data):
        student.new_user.first_name = data["name"]
        # save all tables
        student.save()
        student.new_user.save()


@login_required(login_url=reverse_lazy("login_view"))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy("login_view"))
def student_edit_account(request):
    student = request.user.new_student
    if student.is_independent():
        return HttpResponseRedirect(reverse_lazy("indenpendent_edit_account"))
    else:
        return HttpResponseRedirect(reverse_lazy("school_student_edit_account"))


def username_labeller(request):
    return request.user.username


@login_required(login_url=reverse_lazy("login_view"))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy("login_view"))
@ratelimit(
    "ip",
    labeller=username_labeller,
    periods=["1m"],
    increment=lambda req, res: hasattr(res, "count") and res.count,
)
def student_join_organisation(request):
    increment_count = False

    student = request.user.new_student
    request_form = StudentJoinOrganisationForm()

    # check student not managed by a school
    if student.class_field:
        raise Http404

    if request.method == "POST":
        if "class_join_request" in request.POST:
            increment_count = True
            request_form = StudentJoinOrganisationForm(request.POST)
            if request_form.is_valid():
                student.pending_class_request = request_form.klass
                student.save()

                emailMessage = email_messages.studentJoinRequestSentEmail(
                    request,
                    request_form.klass.teacher.school.name,
                    request_form.klass.access_code,
                )
                send_email(
                    NOTIFICATION_EMAIL,
                    [student.new_user.email],
                    emailMessage["subject"],
                    emailMessage["message"],
                )

                emailMessage = email_messages.studentJoinRequestNotifyEmail(
                    request,
                    student.new_user.username,
                    student.new_user.email,
                    student.pending_class_request.access_code,
                )
                send_email(
                    NOTIFICATION_EMAIL,
                    [student.pending_class_request.teacher.new_user.email],
                    emailMessage["subject"],
                    emailMessage["message"],
                )

                messages.success(
                    request,
                    "Your request to join a school has been received successfully.",
                )

            else:
                request_form = StudentJoinOrganisationForm(request.POST)

        elif "revoke_join_request" in request.POST:
            student.pending_class_request = None
            student.save()
            # Check teacher hasn't since accepted rejection before posting success
            if not student.class_field:
                messages.success(
                    request,
                    "Your request to join a school has been cancelled successfully.",
                )
            return HttpResponseRedirect(reverse_lazy("student_edit_account"))

    res = render(
        request,
        "portal/play/student_join_organisation.html",
        {"request_form": request_form, "student": student},
    )
    res.count = increment_count
    return res
