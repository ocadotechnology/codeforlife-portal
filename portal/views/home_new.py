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

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal.models import Teacher, Class
from portal.forms.teach import TeacherSignupForm, TeacherLoginForm
from portal.helpers.emails_new import send_verification_email, is_verified
from portal.utils import using_two_factor
from portal import app_settings
from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(app_settings.RECAPTCHA_PRIVATE_KEY, app_settings.RECAPTCHA_PUBLIC_KEY)


def teach_email_labeller(request):
    if request.method == 'POST' and 'login' in request.POST:
        return request.POST['login-email']

    return ''


def login_view(request):
    return render_login_form(request)


def logout_view_new(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('home_new'))


def register_view(request):
    return render_signup_form(request)


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('email', labeller=teach_email_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def render_login_form(request):
    invalid_form = False

    limits = getattr(request, 'limits', {'ip': [0], 'email': [0]})
    captcha_limit = 5

    LoginFormWithCaptcha = partial(create_form_subclass_with_recaptcha(TeacherLoginForm, recaptcha_client), request)
    InputLoginForm = compute_input_login_form(LoginFormWithCaptcha, limits, captcha_limit)
    OutputLoginForm = compute_output_login_form(LoginFormWithCaptcha, limits, captcha_limit)

    login_form = OutputLoginForm(prefix='login')

    if request.method == 'POST':
        login_form = InputLoginForm(request.POST, prefix='login')
        if login_form.is_valid():
            return process_login_form(request, login_form)

        else:
            login_form = OutputLoginForm(request.POST, prefix='login')
            invalid_form = True

    res = render(request, 'redesign/login.html', {
        'login_form': login_form,
        'logged_in_as_teacher': is_logged_in_as_teacher(request),
    })

    res.count = invalid_form
    return res


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('email', labeller=teach_email_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def render_signup_form(request):
    invalid_form = False

    signup_form = TeacherSignupForm(prefix='signup')

    if request.method == 'POST':
        signup_form = TeacherSignupForm(request.POST, prefix='signup')
        if signup_form.is_valid():
            data = signup_form.cleaned_data
            return process_signup_form(request, data)

    res = render(request, 'redesign/register.html', {
        'signup_form': signup_form
    })

    res.count = invalid_form
    return res


def compute_use_captcha(limits, captcha_limit):
    using_captcha = (limits['ip'][0] > captcha_limit or limits['email'][0] > captcha_limit)
    return using_captcha


def compute_should_use_captcha(limits, captcha_limit):
    should_use_captcha = (limits['ip'][0] >= captcha_limit or limits['email'][0] >= captcha_limit)
    return should_use_captcha


def compute_input_login_form(LoginFormWithCaptcha, limits, captcha_limit):
    InputLoginForm = LoginFormWithCaptcha if compute_use_captcha(limits, captcha_limit) else TeacherLoginForm
    return InputLoginForm


def compute_output_login_form(LoginFormWithCaptcha, limits, captcha_limit):
    OutputLoginForm = LoginFormWithCaptcha if compute_should_use_captcha(limits, captcha_limit) else TeacherLoginForm
    return OutputLoginForm


def process_login_form(request, login_form):
    user = login_form.user
    if not is_verified(user):
        send_verification_email(request, user)
        return render(request, 'portal/email_verification_needed.html', {'user': user})

    login(request, login_form.user)

    if using_two_factor(request.user):
        return render(request, 'portal/2FA_redirect.html', {
            'form': AuthenticationForm(),
            'username': request.user.username,
            'password': login_form.cleaned_data['password'],
        })
    else:
        link = reverse('two_factor:profile')
        messages.info(
            request, ("You are not currently set up with two-factor authentication. " +
                      "Use your phone or tablet to enhance your account's security. " +
                      "Click <a href='" + link + "'>here</a> to find out more and " +
                      "set it up or go to your account page at any time."),
            extra_tags='safe')

    next_url = request.GET.get('next', None)
    if next_url:
        return HttpResponseRedirect(next_url)

    teacher = request.user.userprofile.teacher

    return redirect_user_to_correct_page(teacher)


def process_signup_form(request, data):
    teacher = Teacher.objects.factory(
        title=data['title'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        password=data['password'])

    send_verification_email(request, teacher.user.user)

    return render(request, 'redesign/email_verification_needed_new.html', {'user': teacher.user.user})


def is_logged_in_as_teacher(request):
    logged_in_as_teacher = hasattr(request.user, 'userprofile') and \
        hasattr(request.user.userprofile, 'teacher') and \
        (request.user.is_verified() or not using_two_factor(request.user))
    return logged_in_as_teacher


def redirect_user_to_correct_page(teacher):
    if teacher.has_school():
        if teacher.has_class():
            classes = Class.objects.filter(teacher=teacher)
            first_class = classes[0]

            if first_class.has_students():
                return HttpResponseRedirect(reverse_lazy('dashboard'))
            else:
                return HttpResponseRedirect(reverse_lazy('onboarding-class', kwargs={'access_code': first_class.access_code}))
        else:
            return HttpResponseRedirect(reverse_lazy('onboarding-classes'))
    else:
        return HttpResponseRedirect(reverse_lazy('onboarding-organisation'))
