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
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic.edit import FormView

from portal.forms.play import StudentEditAccountForm, IndependentStudentEditAccountForm
from portal.helpers.emails import update_email
from portal.helpers.password import check_update_password
from portal.models import Student
from portal.permissions import logged_in_as_student


def _get_form(self, form_class):
    """
    Generic function which gets the appropriate edit account details form for either
    a school student or an independent student.
    :param self: The view class the form is used in.
    :param form_class: The form class which corresponds to the type of student.
    :return: The initialised form which can then be used in the FormView.
    """
    user = self.request.user
    if form_class is None:
        form_class = self.get_form_class()
    return form_class(user, **self.get_form_kwargs())


def _process_form(self, process_function, form, view):
    """
    Generic function which processes the appropriate edit account details form for
    either a school student or an independent student.
    :param self: The view class the form is used in.
    :param process_function: The core function that is needed to process the form.
    :param form: The form which needs to be processed.
    :param view: The view object.
    :return: The view once the form is valid and has been submitted.
    """
    student = self.request.user.new_student
    process_function(form, student, self.request)
    return super(view, self).form_valid(form)


class SchoolStudentEditAccountView(LoginRequiredMixin, FormView):
    """
    A FormView for editing a school student's account details. This forms enables a
    school student to change their password.
    """
    login_url = reverse_lazy("student_login")
    form_class = StudentEditAccountForm
    template_name = "../templates/portal/play/student_edit_account.html"
    success_url = reverse_lazy("student_details")
    model = Student

    def form_valid(self, form):
        return _process_form(
            self,
            self.process_student_edit_account_form,
            form,
            SchoolStudentEditAccountView,
        )

    def process_student_edit_account_form(self, form, student, request):
        data = form.cleaned_data
        # check not default value for CharField
        check_update_password(form, student.new_user, request, data)

        messages.success(
            request, "Your account details have been changed successfully."
        )

    def get_form(self, form_class=None):
        return _get_form(self, form_class)


class IndependentStudentEditAccountView(LoginRequiredMixin, FormView):
    """
    A FormView for editing an independent student's account details. This forms enables
    an independent student to change their name, their email and / or their password.
    """
    login_url = reverse_lazy("independent_student_login")
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
        return _get_form(self, form_class)

    def get_success_url(self):
        if self.changing_email:
            return reverse_lazy("email_verification")
        else:
            return reverse_lazy("student_details")

    def form_valid(self, form):
        return _process_form(
            self,
            self.process_independent_student_edit_account_form,
            form,
            IndependentStudentEditAccountView,
        )

    def process_independent_student_edit_account_form(self, form, student, request):
        data = form.cleaned_data

        # check not default value for CharField
        check_update_password(form, student.new_user, request, data)

        # allow individual students to update more
        self.changing_email, new_email = update_email(student.new_user, request, data)

        self.update_name(student, data)

        messages.success(
            request, "Your account details have been changed successfully."
        )

        if self.changing_email:
            logout(request)

    def update_name(self, student, data):
        student.new_user.first_name = data["name"]
        # save all tables
        student.save()
        student.new_user.save()


@login_required(login_url=reverse_lazy("home"))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy("home"))
def student_edit_account(request):
    student = request.user.new_student
    if student.is_independent():
        return HttpResponseRedirect(reverse_lazy("independent_edit_account"))
    else:
        return HttpResponseRedirect(reverse_lazy("school_student_edit_account"))
