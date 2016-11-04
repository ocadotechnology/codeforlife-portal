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

from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_decode
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth import get_user_model
from two_factor.views import LoginView
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha
from deploy import captcha

from portal.forms.registration import PasswordResetSetPasswordForm, StudentPasswordResetForm, TeacherPasswordResetForm
from portal.permissions import not_logged_in, not_fully_logged_in
from portal.helpers.emails import PASSWORD_RESET_EMAIL
from portal import app_settings
from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(app_settings.RECAPTCHA_PRIVATE_KEY, app_settings.RECAPTCHA_PUBLIC_KEY)

@ratelimit('def', periods=['1m'])
def custom_2FA_login(request):
    block_limit = 5

    if getattr(request, 'limits', { 'def' : [0] })['def'][0] >= block_limit:
        return HttpResponseRedirect(reverse_lazy('locked_out'))

    return LoginView.as_view()(request)


@user_passes_test(not_fully_logged_in, login_url=reverse_lazy('current_user'))
def password_reset_check_and_confirm(request, uidb64=None, token=None, post_reset_redirect=None):
    # Customised standard django auth view with customised form to incorporate checking the password set is strong enough
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user and hasattr(user.userprofile, 'student'):
        usertype = 'STUDENT'
    else:
        usertype = 'TEACHER'
    return password_reset_confirm(request, set_password_form=PasswordResetSetPasswordForm, uidb64=uidb64, token=token, post_reset_redirect=post_reset_redirect, extra_context= { 'usertype': usertype })


@user_passes_test(not_logged_in, login_url=reverse_lazy('current_user'))
def student_password_reset(request, post_reset_redirect):
    form = StudentPasswordResetForm if not captcha.CAPTCHA_ENABLED else decorate_with_captcha(StudentPasswordResetForm, request,
                                                                                   recaptcha_client)
    return password_reset(request, from_email=PASSWORD_RESET_EMAIL, template_name='registration/student_password_reset_form.html', password_reset_form=form, post_reset_redirect=post_reset_redirect, is_admin_site=True)


@user_passes_test(not_fully_logged_in, login_url=reverse_lazy('current_user'))
def teacher_password_reset(request, post_reset_redirect):
    form = TeacherPasswordResetForm if not captcha.CAPTCHA_ENABLED else decorate_with_captcha(TeacherPasswordResetForm, request,
                                                                                   recaptcha_client)
    return password_reset(request, from_email=PASSWORD_RESET_EMAIL, template_name='registration/teacher_password_reset_form.html', password_reset_form=form, post_reset_redirect=post_reset_redirect, is_admin_site=True)


def decorate_with_captcha(base_class, request, recaptcha_client):
    form_with_captcha_class = create_form_subclass_with_recaptcha(base_class, recaptcha_client)

    class FormWithCaptcha(form_with_captcha_class):

        def __init__(self, *args, **kwargs):
            super(FormWithCaptcha, self).__init__(request, *args, **kwargs)

    return FormWithCaptcha
