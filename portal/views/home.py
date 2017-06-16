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
from functools import partial

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal.models import Teacher, Class, Student
from portal.forms.teach import TeacherSignupForm, TeacherLoginForm
from portal.forms.play import StudentLoginForm, IndependentStudentLoginForm, StudentSignupForm
from portal.helpers.emails import send_verification_email, is_verified, send_email, CONTACT_EMAIL
from portal.app_settings import CONTACT_FORM_EMAILS
from portal.utils import using_two_factor
from portal import app_settings, emailMessages
from ratelimit.decorators import ratelimit
from portal.forms.home import ContactForm

recaptcha_client = RecaptchaClient(app_settings.RECAPTCHA_PRIVATE_KEY, app_settings.RECAPTCHA_PUBLIC_KEY)


def teach_email_labeller(request):
    if request.method == 'POST' and 'login_view' in request.POST:
        return request.POST['login-teacher_email']

    return ''


def play_name_labeller(request):
    if request.method == 'POST':
        if 'school_login' in request.POST:
            return request.POST['login-name'] + ':' + request.POST['login-access_code']

        if 'independent_student_login' in request.POST:
            return request.POST['independent_student-username']

    return ''


def login_view(request):
    return render_login_form(request)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy('home'))


def register_view(request):
    return render_signup_form(request)


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('email', labeller=teach_email_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('name', labeller=play_name_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def render_login_form(request):
    invalid_form = False

    teacher_limits = getattr(request, 'limits', {'ip': [0], 'email': [0]})
    teacher_captcha_limit = 5

    LoginFormWithCaptcha = partial(create_form_subclass_with_recaptcha(TeacherLoginForm, recaptcha_client), request)
    InputLoginForm = compute_teacher_input_login_form(LoginFormWithCaptcha, teacher_limits, teacher_captcha_limit)
    OutputLoginForm = compute_teacher_output_login_form(LoginFormWithCaptcha, teacher_limits, teacher_captcha_limit)

    login_form = OutputLoginForm(prefix='login')

    student_limits = getattr(request, 'limits', {'ip': [0], 'name': [0]})
    student_captcha_limit = 30
    student_name_captcha_limit = 5

    StudentLoginFormWithCaptcha = partial(create_form_subclass_with_recaptcha(StudentLoginForm, recaptcha_client), request)
    InputStudentLoginForm = compute_student_input_login_form(StudentLoginFormWithCaptcha, student_limits, student_captcha_limit, student_name_captcha_limit)
    OutputStudentLoginForm = compute_student_output_login_form(StudentLoginFormWithCaptcha, student_limits, student_captcha_limit, student_name_captcha_limit)

    school_login_form = OutputStudentLoginForm(prefix='login')

    IndependentStudentLoginFormWithCaptcha = partial(create_form_subclass_with_recaptcha(IndependentStudentLoginForm, recaptcha_client), request)
    InputIndependentStudentLoginForm = compute_indep_student_input_login_form(IndependentStudentLoginFormWithCaptcha, student_limits, student_captcha_limit, student_name_captcha_limit)
    OutputIndependentStudentLoginForm = compute_indep_student_output_login_form(IndependentStudentLoginFormWithCaptcha, student_limits, student_captcha_limit, student_name_captcha_limit)

    independent_student_login_form = IndependentStudentLoginForm(prefix='independent_student')
    independent_student_view = False

    render_dict = {
        'login_form': login_form,
        'school_login_form': school_login_form,
        'independent_student_login_form': independent_student_login_form,
        'independent_student_view': independent_student_view,
        'logged_in_as_teacher': is_logged_in_as_teacher(request),
    }

    if request.method == 'POST':
        if 'school_login' in request.POST:
            form = InputStudentLoginForm(request.POST, prefix="login")
            process_form = process_student_login_form
            render_dict['school_login_form'] = OutputStudentLoginForm(request.POST, prefix='login')

        elif 'independent_student_login' in request.POST:
            form = InputIndependentStudentLoginForm(request.POST, prefix='independent_student')
            process_form = process_indep_student_login_form
            render_dict['independent_student_login_form'] = OutputIndependentStudentLoginForm(request.POST, prefix='independent_student')
            render_dict['independent_student_view'] = True

        else:
            form = InputLoginForm(request.POST, prefix='login')
            process_form = process_login_form
            render_dict['login_form'] = OutputLoginForm(request.POST, prefix='login')

        if form.is_valid():
            return process_form(request, form)
        else:
            invalid_form = True

    res = render(request, 'portal/login.html', render_dict)

    res.count = invalid_form
    return res


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('email', labeller=teach_email_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
@ratelimit('name', labeller=play_name_labeller, ip=False, periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def render_signup_form(request):
    invalid_form = False

    teacher_signup_form = TeacherSignupForm(prefix='teacher_signup')
    student_signup_form = StudentSignupForm(prefix='student_signup')

    if request.method == 'POST':
        if 'teacher_signup' in request.POST:
            teacher_signup_form = TeacherSignupForm(request.POST, prefix='teacher_signup')
            if teacher_signup_form.is_valid():
                data = teacher_signup_form.cleaned_data
                return process_signup_form(request, data)

        else:
            student_signup_form = StudentSignupForm(request.POST, prefix='student_signup')
            if student_signup_form.is_valid():
                data = student_signup_form.cleaned_data
                return process_student_signup_form(request, data)

    res = render(request, 'portal/register.html', {
        'teacher_signup_form': teacher_signup_form,
        'student_signup_form': student_signup_form,
    })

    res.count = invalid_form
    return res


def compute_teacher_use_captcha(limits, captcha_limit):
    using_captcha = (limits['ip'][0] > captcha_limit or limits['email'][0] > captcha_limit)
    return using_captcha


def compute_teacher_should_use_captcha(limits, captcha_limit):
    should_use_captcha = (limits['ip'][0] >= captcha_limit or limits['email'][0] >= captcha_limit)
    return should_use_captcha


def compute_student_use_captcha(limits, ip_captcha_limit, name_captcha_limit):
    using_captcha = (limits['ip'][0] > ip_captcha_limit or limits['name'][0] >= name_captcha_limit)
    return using_captcha


def compute_student_should_use_captcha(limits, ip_captcha_limit, name_captcha_limit):
    should_use_captcha = (limits['ip'][0] >= ip_captcha_limit or limits['name'][0] >= name_captcha_limit)
    return should_use_captcha


def compute_teacher_input_login_form(LoginFormWithCaptcha, limits, captcha_limit):
    InputLoginForm = LoginFormWithCaptcha if compute_teacher_use_captcha(limits, captcha_limit) else TeacherLoginForm
    return InputLoginForm


def compute_teacher_output_login_form(LoginFormWithCaptcha, limits, captcha_limit):
    OutputLoginForm = LoginFormWithCaptcha if compute_teacher_should_use_captcha(limits, captcha_limit) else TeacherLoginForm
    return OutputLoginForm


def compute_student_input_login_form(StudentLoginFormWithCaptcha, limits, ip_captcha_limit, name_captcha_limit):
    InputStudentLoginForm = StudentLoginFormWithCaptcha if compute_student_use_captcha(limits, ip_captcha_limit, name_captcha_limit) else StudentLoginForm
    return InputStudentLoginForm


def compute_student_output_login_form(StudentLoginFormWithCaptcha, limits, ip_captcha_limit, name_captcha_limit):
    OutputStudentLoginForm = StudentLoginFormWithCaptcha if compute_student_should_use_captcha(limits, ip_captcha_limit, name_captcha_limit) else StudentLoginForm
    return OutputStudentLoginForm


def compute_indep_student_input_login_form(IndependentStudentLoginFormWithCaptcha, limits, ip_captcha_limit, name_captcha_limit):
    InputIndependentStudentLoginForm = IndependentStudentLoginFormWithCaptcha if compute_student_use_captcha(limits, ip_captcha_limit, name_captcha_limit) else IndependentStudentLoginForm
    return InputIndependentStudentLoginForm


def compute_indep_student_output_login_form(IndependentStudentLoginFormWithCaptcha, limits, ip_captcha_limit, name_captcha_limit):
    OutputIndependentStudentLoginForm = IndependentStudentLoginFormWithCaptcha if compute_student_should_use_captcha(limits, ip_captcha_limit, name_captcha_limit) else IndependentStudentLoginForm
    return OutputIndependentStudentLoginForm


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
            'password': login_form.cleaned_data['teacher_password'],
        })

    next_url = request.GET.get('next', None)
    if next_url:
        return HttpResponseRedirect(next_url)

    teacher = request.user.userprofile.teacher

    return redirect_user_to_correct_page(request, teacher)


def process_student_login_form(request, school_login_form):
    login(request, school_login_form.user)

    next_url = request.GET.get('next', None)
    if next_url:
        return HttpResponseRedirect(next_url)

    return HttpResponseRedirect(reverse_lazy('student_details'))


def process_indep_student_login_form(request, independent_student_login_form):
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


def process_signup_form(request, data):
    teacher = Teacher.objects.factory(
        title=data['teacher_title'],
        first_name=data['teacher_first_name'],
        last_name=data['teacher_last_name'],
        email=data['teacher_email'],
        password=data['teacher_password'])

    send_verification_email(request, teacher.user.user)

    return render(request, 'portal/email_verification_needed.html', {'user': teacher.user.user})


def process_student_signup_form(request, data):
    student = Student.objects.independentStudentFactory(
        username=data['username'],
        name=data['name'],
        email=data['email'],
        password=data['password'])

    email_supplied = (data['email'] != '')
    if email_supplied:
        send_verification_email(request, student.new_user)
        return render(request, 'portal/email_verification_needed.html', {'user': student.new_user})

    return render(request, 'portal/play/student_details.html')


def is_logged_in_as_teacher(request):
    logged_in_as_teacher = hasattr(request.user, 'userprofile') and \
        hasattr(request.user.userprofile, 'teacher') and \
        (request.user.is_verified() or not using_two_factor(request.user))
    return logged_in_as_teacher


def redirect_user_to_correct_page(request, teacher):
    if teacher.has_school():
        classes = teacher.class_teacher.all()
        if classes:
            classes_count = classes.count()
            if classes_count > 1 or classes[0].has_students():
                link = reverse('two_factor:profile')
                messages.info(
                    request, ("You are not currently set up with two-factor authentication. " +
                              "Use your phone or tablet to enhance your account's security.</br>" +
                              "Click <a href='" + link + "'>here</a> to find out more and " +
                              "set it up or go to your account page at any time."),
                    extra_tags='safe')
                return HttpResponseRedirect(reverse_lazy('dashboard'))
            else:
                return HttpResponseRedirect(reverse_lazy('onboarding-class',
                                                         kwargs={'access_code': classes[0].access_code}))
        else:
            return HttpResponseRedirect(reverse_lazy('onboarding-classes'))
    else:
        return HttpResponseRedirect(reverse_lazy('onboarding-organisation'))


@ratelimit('ip', periods=['1m'], increment=lambda req, res: hasattr(res, 'count') and res.count)
def contact(request):
    increment_count = False
    limits = getattr(request, 'limits', {'ip': [0]})
    captcha_limit = 5

    using_captcha = (limits['ip'][0] > captcha_limit)
    should_use_captcha = (limits['ip'][0] >= captcha_limit)

    ContactFormWithCaptcha = partial(create_form_subclass_with_recaptcha(ContactForm, recaptcha_client), request)
    InputContactForm = ContactFormWithCaptcha if using_captcha else ContactForm
    OutputContactForm = ContactFormWithCaptcha if should_use_captcha else ContactForm

    anchor = ''

    if request.method == 'POST':
        contact_form = InputContactForm(request.POST)
        increment_count = True

        if contact_form.is_valid():
            email_message = emailMessages.contactEmail(
                request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'],
                contact_form.cleaned_data['email'], contact_form.cleaned_data['message'],
                contact_form.cleaned_data['browser'])
            send_email(CONTACT_EMAIL, CONTACT_FORM_EMAILS, email_message['subject'], email_message['message'])

            confirmed_email_message = emailMessages.confirmationContactEmailMessage(
                request, contact_form.cleaned_data['name'], contact_form.cleaned_data['telephone'],
                contact_form.cleaned_data['email'], contact_form.cleaned_data['message'])
            send_email(CONTACT_EMAIL, [contact_form.cleaned_data['email']],
                       confirmed_email_message['subject'], confirmed_email_message['message'])

            messages.success(request, 'Your message was sent successfully.')
            return HttpResponseRedirect('.')
        else:
            contact_form = OutputContactForm(request.POST)
            anchor = "contact"

    else:
        contact_form = OutputContactForm()

    response = render(request, 'portal/help-and-support.html',
                      {'form': contact_form,
                       'anchor': anchor})

    response.count = increment_count
    return response
