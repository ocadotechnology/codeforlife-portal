# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2017, Ocado Innovation Limited
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

import warnings

from django.contrib.auth.forms import (
    PasswordResetForm, SetPasswordForm,
)
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.utils.encoding import force_text
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse
from django.utils.deprecation import RemovedInDjango20Warning
from django.utils.translation import ugettext as _
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha
from deploy import captcha
from two_factor.views import LoginView

from portal.forms.registration import TeacherPasswordResetForm, PasswordResetSetPasswordForm, \
    StudentPasswordResetForm
from portal.permissions import not_logged_in, not_fully_logged_in
from portal.helpers.emails import PASSWORD_RESET_EMAIL
from portal import app_settings
from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(app_settings.RECAPTCHA_PRIVATE_KEY, app_settings.RECAPTCHA_PUBLIC_KEY)


@ratelimit('def', periods=['1m'])
def custom_2FA_login(request):
    block_limit = 5

    if getattr(request, 'limits', {'def': [0]})['def'][0] >= block_limit:
        return HttpResponseRedirect(reverse_lazy('locked_out'))

    return LoginView.as_view()(request)


@user_passes_test(not_logged_in, login_url=reverse_lazy('login_view'))
def student_password_reset(request):
    usertype = "STUDENT"
    form = (StudentPasswordResetForm if not captcha.CAPTCHA_ENABLED
            else decorate_with_captcha(StudentPasswordResetForm, request, recaptcha_client))
    return password_reset(request, usertype, from_email=PASSWORD_RESET_EMAIL, template_name='portal/reset_password_student.html',
                          password_reset_form=form, is_admin_site=True)


@user_passes_test(not_fully_logged_in, login_url=reverse_lazy('login_view'))
def teacher_password_reset(request):
    usertype = "TEACHER"
    form = (TeacherPasswordResetForm if not captcha.CAPTCHA_ENABLED
            else decorate_with_captcha(TeacherPasswordResetForm, request, recaptcha_client))
    return password_reset(request, usertype, from_email=PASSWORD_RESET_EMAIL, template_name='portal/reset_password_teach.html',
                          password_reset_form=form, is_admin_site=True)


def decorate_with_captcha(base_class, request, recaptcha_client):
    form_with_captcha_class = create_form_subclass_with_recaptcha(base_class, recaptcha_client)

    class FormWithCaptcha(form_with_captcha_class):

        def __init__(self, *args, **kwargs):
            super(FormWithCaptcha, self).__init__(request, *args, **kwargs)

    return FormWithCaptcha


@csrf_protect
def password_reset(request, usertype, is_admin_site=False, template_name='portal/reset_password_teach.html',
                   email_template_name='portal/reset_password_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm, token_generator=default_token_generator,
                   from_email=None, current_app=None, extra_context=None, html_email_template_name=None):
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
            }
            if is_admin_site:
                warnings.warn(
                    "The is_admin_site argument to "
                    "django.contrib.auth.views.password_reset() is deprecated "
                    "and will be removed in Django 2.0.", RemovedInDjango20Warning, 3
                )
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)

            return render(request, 'portal/reset_password_email_sent.html', {'usertype': usertype})
    else:
        form = password_reset_form()

    context = {
        'form': form,
        'title': _('Password reset'),
    }

    update_context_and_apps(request, context, current_app, extra_context)

    return TemplateResponse(request, template_name, context)


def update_context_and_apps(request, context, current_app, extra_context):
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app


def password_reset_done(request, template_name='portal/reset_password_email_sent.html', current_app=None, extra_context=None):
    context = {
        'title': _('Password reset sent'),
    }

    update_context_and_apps(request, context, current_app, extra_context)

    return TemplateResponse(request, template_name, context)


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, usertype, uidb64=None, token=None,
                           template_name='portal/reset_password_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm, current_app=None, extra_context=None):
    """
    View that checks the hash in a password reset link and presents a
    form for entering a new password.
    """
    UserModel = get_user_model()
    check_uidb64(uidb64, token)

    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user_is_authenticated(user, token_generator, token):
        validlink = True
        title = _('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return render(request, 'portal/reset_password_done.html', {'usertype': usertype})
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _('Password reset unsuccessful')

    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }

    update_context_and_apps(request, context, current_app, extra_context)

    return TemplateResponse(request, template_name, context)


def check_uidb64(uidb64, token):
    assert uidb64 is not None and token is not None  # checked by URLconf


def user_is_authenticated(user, token_generator, token):
    return user is not None and token_generator.check_token(user, token)


@user_passes_test(not_fully_logged_in, login_url=reverse_lazy('login_view'))
def password_reset_check_and_confirm(request, uidb64=None, token=None):
    """
    Customised standard django auth view with customised form to incorporate checking the password set is strong enough
    """
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user and hasattr(user, 'new_student'):
        usertype = 'STUDENT'
    else:
        usertype = 'TEACHER'
    return password_reset_confirm(request, usertype, set_password_form=PasswordResetSetPasswordForm, uidb64=uidb64,
                                  token=token, extra_context={'usertype': usertype})
