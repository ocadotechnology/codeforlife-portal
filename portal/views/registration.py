# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2021, Ocado Innovation Limited
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
from common.helpers.emails import PASSWORD_RESET_EMAIL
from common.models import Teacher, Student
from common.permissions import not_logged_in, not_fully_logged_in
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from deploy import captcha
from portal import app_settings
from portal.forms.registration import (
    TeacherPasswordResetForm,
    PasswordResetSetPasswordForm,
    StudentPasswordResetForm,
)
from portal.helpers.captcha import remove_captcha_from_form
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user


@user_passes_test(not_logged_in, login_url=reverse_lazy("home"))
def student_password_reset(request):
    usertype = "STUDENT"
    return password_reset(
        request,
        usertype,
        from_email=PASSWORD_RESET_EMAIL,
        template_name="portal/reset_password_student.html",
        password_reset_form=StudentPasswordResetForm,
    )


@user_passes_test(not_fully_logged_in, login_url=reverse_lazy("teacher_login"))
def teacher_password_reset(request):
    usertype = "TEACHER"
    return password_reset(
        request,
        usertype,
        from_email=PASSWORD_RESET_EMAIL,
        template_name="portal/reset_password_teach.html",
        password_reset_form=TeacherPasswordResetForm,
    )


@csrf_protect
def password_reset(
    request,
    usertype,
    template_name="portal/reset_password_teach.html",
    email_template_name="portal/reset_password_email.html",
    subject_template_name="registration/password_reset_subject.txt",
    password_reset_form=PasswordResetForm,
    token_generator=default_token_generator,
    from_email=None,
    current_app=None,
    extra_context=None,
    html_email_template_name=None,
):
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if not captcha.CAPTCHA_ENABLED:
            remove_captcha_from_form(form)
        if form.is_valid():
            opts = {
                "use_https": request.is_secure(),
                "token_generator": token_generator,
                "from_email": from_email,
                "email_template_name": email_template_name,
                "subject_template_name": subject_template_name,
                "request": request,
                "html_email_template_name": html_email_template_name,
            }
            form.save(**opts)

            return render(
                request, "portal/reset_password_email_sent.html", {"usertype": usertype}
            )
    else:
        form = password_reset_form()

    if not captcha.CAPTCHA_ENABLED:
        remove_captcha_from_form(form)

    context = {
        "form": form,
        "title": _("Password reset"),
        "settings": app_settings,
        "should_use_recaptcha": captcha.CAPTCHA_ENABLED,
    }

    update_context_and_apps(request, context, current_app, extra_context)

    return TemplateResponse(request, template_name, context)


def update_context_and_apps(request, context, current_app, extra_context):
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app


def password_reset_done(
    request,
    template_name="portal/reset_password_email_sent.html",
    current_app=None,
    extra_context=None,
):
    context = {"title": _("Password reset sent")}

    update_context_and_apps(request, context, current_app, extra_context)

    return TemplateResponse(request, template_name, context)


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(
    request,
    usertype,
    uidb64=None,
    token=None,
    template_name="portal/reset_password_confirm.html",
    token_generator=default_token_generator,
    set_password_form=SetPasswordForm,
    current_app=None,
    extra_context=None,
):
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
        title = _("Enter new password")
        if request.method == "POST":
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()

                # Reset ratelimit cache upon successful password reset
                clear_ratelimit_cache_for_user(user.username)

                _check_and_unblock_user(user.username, usertype)

                return render(
                    request, "portal/reset_password_done.html", {"usertype": usertype}
                )
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _("Password reset unsuccessful")

    context = {"form": form, "title": title, "validlink": validlink}

    update_context_and_apps(request, context, current_app, extra_context)

    return TemplateResponse(request, template_name, context)


def _check_and_unblock_user(username, usertype):
    if usertype == "TEACHER":
        user = Teacher.objects.get(new_user__username=username)
    else:
        user = Student.objects.get(new_user__username=username)

    if user.blocked_time is not None:
        user.blocked_time = None
        user.save()


def check_uidb64(uidb64, token):
    assert uidb64 is not None and token is not None  # checked by URLconf


def user_is_authenticated(user, token_generator, token):
    return user is not None and token_generator.check_token(user, token)


@user_passes_test(not_fully_logged_in, login_url=reverse_lazy("home"))
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
    if user and hasattr(user, "new_student"):
        usertype = "STUDENT"
    else:
        usertype = "TEACHER"
    return password_reset_confirm(
        request,
        usertype,
        set_password_form=PasswordResetSetPasswordForm,
        uidb64=uidb64,
        token=token,
        extra_context={"usertype": usertype},
    )
