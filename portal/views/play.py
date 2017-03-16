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
from recaptcha import RecaptchaClient

from django.shortcuts import render
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal.forms.play import StudentEditAccountForm, StudentJoinOrganisationForm
from portal.permissions import logged_in_as_student
from portal.helpers.emails import send_email, send_verification_email, NOTIFICATION_EMAIL
from portal import app_settings, emailMessages

from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(app_settings.RECAPTCHA_PRIVATE_KEY, app_settings.RECAPTCHA_PUBLIC_KEY)


@login_required(login_url=reverse_lazy('play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('play'))
def student_details(request):
    return render(request, 'portal/play/student_details.html')


@login_required(login_url=reverse_lazy('play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('play'))
def student_edit_account(request):
    student = request.user.student

    if request.method == 'POST':
        form = StudentEditAccountForm(request.user, request.POST)
        if form.is_valid():
            data = form.cleaned_data
            changing_email = False

            # check not default value for CharField
            if (data['password'] != ''):
                student.user.set_password(data['password'])
                student.user.save()
                update_session_auth_hash(request, form.user)

            # allow individual students to update more
            if not student.class_field:
                new_email = data['email']
                if new_email != '' and new_email != student.user.email:
                    # new email to set and verify
                    changing_email = True
                    send_verification_email(request, student.user, new_email)

                student.user.first_name = data['name']
                # save all tables
                student.save()
                student.user.save()

            messages.success(request, 'Your account details have been changed successfully.')

            if changing_email:
                logout(request)
                return render(request, 'portal/email_verification_needed.html', {'userprofile': student.user, 'email': new_email})

            return HttpResponseRedirect(reverse_lazy('student_details'))
    else:
        form = StudentEditAccountForm(request.user, initial={
            'name': student.user.first_name})

    return render(request, 'portal/play/student_edit_account.html', {'form': form})


def username_labeller(request):
    return request.user.username


@login_required(login_url=reverse_lazy('play'))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy('play'))
@ratelimit('ip', labeller=username_labeller, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def student_join_organisation(request):
    increment_count = False
    limits = getattr(request, 'limits', {'ip': [0]})
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit)

    StudentJoinOrganisationFormWithCaptcha = partial(create_form_subclass_with_recaptcha(StudentJoinOrganisationForm, recaptcha_client), request)
    InputStudentJoinOrganisationForm = StudentJoinOrganisationFormWithCaptcha if using_captcha else StudentJoinOrganisationForm
    OutputStudentJoinOrganisationForm = StudentJoinOrganisationFormWithCaptcha if should_use_captcha else StudentJoinOrganisationForm

    student = request.user.student
    request_form = OutputStudentJoinOrganisationForm()

    # check student not managed by a school
    if student.class_field:
        raise Http404

    if request.method == 'POST':
        if 'class_join_request' in request.POST:
            increment_count = True
            request_form = InputStudentJoinOrganisationForm(request.POST)
            if request_form.is_valid():
                student.pending_class_request = request_form.klass
                student.save()

                emailMessage = emailMessages.studentJoinRequestSentEmail(request, request_form.klass.teacher.school.name, request_form.klass.access_code)
                send_email(NOTIFICATION_EMAIL, [student.user.email], emailMessage['subject'], emailMessage['message'])

                emailMessage = emailMessages.studentJoinRequestNotifyEmail(request, student.user.username, student.user.email, student.pending_class_request.access_code)
                send_email(NOTIFICATION_EMAIL, [student.pending_class_request.teacher.user.email], emailMessage['subject'], emailMessage['message'])

                messages.success(request, 'Your request to join a school has been received successfully.')

            else:
                request_form = OutputStudentJoinOrganisationForm(request.POST)

        elif 'revoke_join_request' in request.POST:
            student.pending_class_request = None
            student.save()
            # Check teacher hasn't since accepted rejection before posting success message
            if not student.class_field:
                messages.success(request, 'Your request to join a school has been cancelled successfully.')
            return HttpResponseRedirect(reverse_lazy('student_edit_account'))

    res = render(request, 'portal/play/student_join_organisation.html',
                 {'request_form': request_form, 'student': student})

    res.count = increment_count
    return res
