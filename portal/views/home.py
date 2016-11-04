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

from django.core.cache import cache
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal.models import Teacher, Student, FrontPageNews
from portal.forms.home import ContactForm
from portal.forms.teach import TeacherSignupForm, TeacherLoginForm
from portal.forms.play import StudentLoginForm, IndependentStudentLoginForm, StudentSignupForm
from portal.helpers.emails import send_email, send_verification_email, is_verified, CONTACT_EMAIL
from portal.app_settings import CONTACT_FORM_EMAILS
from portal.utils import using_two_factor
from portal import app_settings, emailMessages
from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(app_settings.RECAPTCHA_PRIVATE_KEY, app_settings.RECAPTCHA_PUBLIC_KEY)


def teach_email_labeller(request):
    if request.method == 'POST' and 'login' in request.POST:
        return request.POST['login-email']

    return ''


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('email', labeller=teach_email_labeller, ip=False, periods=['1m'], increment=lambda req,
           res: hasattr(res, 'count') and res.count)
def teach(request):
    invalid_form = False
    limits = getattr(request, 'limits', {'ip': [0], 'email': [0]})
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit or limits['email'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit or limits['email'][0] >= captcha_limit)

    LoginFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(TeacherLoginForm, recaptcha_client), request)
    InputLoginForm = LoginFormWithCaptcha if using_captcha else TeacherLoginForm
    OutputLoginForm = LoginFormWithCaptcha if should_use_captcha else TeacherLoginForm

    login_form = OutputLoginForm(prefix='login')
    signup_form = TeacherSignupForm(prefix='signup')

    if request.method == 'POST':
        if 'login' in request.POST:
            login_form = InputLoginForm(request.POST, prefix='login')
            if login_form.is_valid():
                user = login_form.user
                if not is_verified(user):
                    send_verification_email(request, user)
                    return render(request, 'portal/email_verification_needed.html',
                                  {'user': user})

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
                        request, ("You are not currently set up with two-factor authentication. "
                                  + "Use your phone or tablet to enhance your account's security. "
                                  + "Click <a href='" + link + "'>here</a> to find out more and "
                                  + "set it up or go to your account page at any time."),
                        extra_tags='safe')

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse_lazy('teacher_home'))

            else:
                login_form = OutputLoginForm(request.POST, prefix='login')
                invalid_form = True

        if 'signup' in request.POST:
            signup_form = TeacherSignupForm(request.POST, prefix='signup')
            if signup_form.is_valid():
                data = signup_form.cleaned_data

                teacher = Teacher.objects.factory(
                    title=data['title'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    password=data['password'])

                send_verification_email(request, teacher.user.user)

                return render(request, 'portal/email_verification_needed.html',
                              {'user': teacher.user.user})

    logged_in_as_teacher = hasattr(request.user, 'userprofile') and \
        hasattr(request.user.userprofile, 'teacher') and \
        (request.user.is_verified() or not using_two_factor(request.user))

    res = render(request, 'portal/teach.html', {
        'login_form': login_form,
        'signup_form': signup_form,
        'logged_in_as_teacher': logged_in_as_teacher,
    })

    res.count = invalid_form
    return res


def play_name_labeller(request):
    if request.method == 'POST':
        if 'school_login' in request.POST:
            return request.POST['login-name'] + ':' + request.POST['login-access_code']

        if 'independent_student_login' in request.POST:
            return request.POST['independent_student-username']

    return ''


@ratelimit('ip', periods=['2m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('name', labeller=play_name_labeller, ip=False, periods=['1m'], increment=lambda req,
           res: hasattr(res, 'count') and res.count)
def play(request):
    invalid_form = False
    limits = getattr(request, 'limits', {'ip': [0], 'name': [0]})
    ip_captcha_limit = 30
    name_captcha_limit = 5

    using_captcha = (limits['ip'][0] > ip_captcha_limit or limits['name'][0] >= name_captcha_limit)
    should_use_captcha = (limits['ip'][0] >= ip_captcha_limit or limits['name'][0] >= name_captcha_limit)

    StudentLoginFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(StudentLoginForm, recaptcha_client), request)
    InputStudentLoginForm = StudentLoginFormWithCaptcha if using_captcha else StudentLoginForm
    OutputStudentLoginForm = StudentLoginFormWithCaptcha if should_use_captcha else StudentLoginForm

    IndependentStudentLoginFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(IndependentStudentLoginForm, recaptcha_client), request)
    InputIndependentStudentLoginForm = IndependentStudentLoginFormWithCaptcha if using_captcha else IndependentStudentLoginForm
    OutputIndependentStudentLoginForm = IndependentStudentLoginFormWithCaptcha if should_use_captcha else IndependentStudentLoginForm

    school_login_form = OutputStudentLoginForm(prefix='login')
    independent_student_login_form = IndependentStudentLoginForm(prefix='independent_student')
    signup_form = StudentSignupForm(prefix='signup')

    independent_student_view = False
    signup_view = False
    if request.method == 'POST':
        if 'school_login' in request.POST:
            school_login_form = InputStudentLoginForm(request.POST, prefix='login')
            if school_login_form.is_valid():
                login(request, school_login_form.user)

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse_lazy('student_details'))

            else:
                school_login_form = OutputStudentLoginForm(request.POST, prefix='login')
                invalid_form = True

        elif 'independent_student_login' in request.POST:
            independent_student_login_form = InputIndependentStudentLoginForm(request.POST, prefix='independent_student')
            if independent_student_login_form.is_valid():
                user = independent_student_login_form.user
                if not is_verified(user):
                    send_verification_email(request, user)
                    return render(request, 'portal/email_verification_needed.html',
                                  {'user': user})

                login(request, independent_student_login_form.user)

                next_url = request.GET.get('next', None)
                if next_url:
                    return HttpResponseRedirect(next_url)

                return HttpResponseRedirect(reverse_lazy('student_details'))
            else:
                independent_student_view = True
                independent_student_login_form = OutputIndependentStudentLoginForm(request.POST, prefix='independent_student')
                school_login_form = StudentLoginForm(prefix='login')
                invalid_form = True

        elif 'signup' in request.POST:
            signup_form = StudentSignupForm(request.POST, prefix='signup')
            if signup_form.is_valid():
                data = signup_form.cleaned_data

                student = Student.objects.independentStudentFactory(
                    username=data['username'],
                    name=data['name'],
                    email=data['email'],
                    password=data['password'])

                email_supplied = (data['email'] != '')
                if (email_supplied):
                    send_verification_email(request, student.user.user)
                    return render(request, 'portal/email_verification_needed.html',
                                  {'user': student.user.user})
                else:  # dead code - frontend ensures email supplied.
                    auth_user = authenticate(username=data['username'], password=data['password'])
                    login(request, auth_user)

                return render(request, 'portal/play/student_details.html')
            else:
                signup_view = True

    res = render(request, 'portal/play.html', {
        'school_login_form': school_login_form,
        'independent_student_login_form': independent_student_login_form,
        'signup_form': signup_form,
        'independent_student_view': independent_student_view,
        'signup_view': signup_view,
    })

    res.count = invalid_form
    return res


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def contact(request):
    increment_count = False
    limits = getattr(request, 'limits', {'ip': [0]})
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit)

    ContactFormWithCaptcha = partial(
        create_form_subclass_with_recaptcha(ContactForm, recaptcha_client), request)
    InputContactForm = ContactFormWithCaptcha if using_captcha else ContactForm
    OutputContactForm = ContactFormWithCaptcha if should_use_captcha else ContactForm

    if request.method == 'POST':
        contact_form = InputContactForm(request.POST)
        increment_count = True

        if contact_form.is_valid():
            emailMessage = emailMessages.contactEmail(
                request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'],
                contact_form.cleaned_data['email'], contact_form.cleaned_data['message'],
                contact_form.cleaned_data['browser'])
            send_email(CONTACT_EMAIL, CONTACT_FORM_EMAILS, emailMessage['subject'],
                       emailMessage['message'])

            confirmedEmailMessage = emailMessages.confirmationContactEmailMessage(
                request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'],
                contact_form.cleaned_data['email'], contact_form.cleaned_data['message'])
            send_email(CONTACT_EMAIL, [contact_form.cleaned_data['email']],
                       confirmedEmailMessage['subject'], confirmedEmailMessage['message'])

            messages.success(request, 'Your message was sent successfully.')
            return HttpResponseRedirect('.')

        else:
            contact_form = OutputContactForm(request.POST)

    else:
        contact_form = OutputContactForm()

    response = render(request, 'portal/contact.html', {'form': contact_form})

    response.count = increment_count
    return response


def current_user(request):
    if not hasattr(request.user, 'userprofile'):
        return HttpResponseRedirect(reverse_lazy('home'))
    u = request.user.userprofile
    if hasattr(u, 'student'):
        return HttpResponseRedirect(reverse_lazy('student_details'))
    elif hasattr(u, 'teacher'):
        return HttpResponseRedirect(reverse_lazy('teacher_home'))
    else:
        # default to homepage and logout if something goes wrong
        logout(request)
        return HttpResponseRedirect(reverse_lazy('home'))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('home'))


def get_news():
    key = "front_page_cache"
    results = cache.get(key)
    if results is None:
        results = FrontPageNews.objects.order_by('-added_dstamp')
        cache.set(key, results, 600)
    return results


def home_view(request):
    return render(request, 'portal/home.html', {'news': get_news()})
