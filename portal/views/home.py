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
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.html import escape
from django.utils.http import is_safe_url
from django.views.decorators.cache import cache_control
from django.views.decorators.csrf import csrf_exempt

from deploy import captcha
from portal import app_settings, email_messages
from portal.forms.newsletter_form import NewsletterForm
from portal.forms.play import (
    StudentLoginForm,
    IndependentStudentLoginForm,
    IndependentStudentSignupForm,
)
from portal.forms.teach import TeacherSignupForm, TeacherLoginForm
from portal.helpers.captcha import remove_captcha_from_forms
from portal.helpers.emails import (
    send_verification_email,
    is_verified,
    send_email,
    NOTIFICATION_EMAIL,
    add_to_dotmailer,
)
from portal.models import Teacher, Student
from portal.permissions import logged_in_as_student, logged_in_as_teacher
from portal.strings.home_learning import HOME_LEARNING_BANNER
from portal.utils import using_two_factor


def teach_email_labeller(request):
    if request.method == "POST" and "login_view" in request.POST:
        return request.POST["login-teacher_email"]

    return ""


def play_name_labeller(request):
    if request.method == "POST":
        if "school_login" in request.POST:
            return request.POST["login-name"] + ":" + request.POST["login-access_code"]

        if "independent_student_login" in request.POST:
            return request.POST["independent_student-username"]

    return ""


def login_view(request):
    if request.user.is_authenticated():
        return redirect_user_to_dashboard(request)
    else:
        return render_login_form(request)


def register_view(request):
    if request.user.is_authenticated():
        return redirect_user_to_dashboard(request)
    else:
        return render_signup_form(request)


def redirect_user_to_dashboard(request):
    if logged_in_as_student(request.user):
        return HttpResponseRedirect(reverse_lazy("student_details"))
    elif logged_in_as_teacher(request.user):
        return HttpResponseRedirect(reverse_lazy("dashboard"))
    else:
        return HttpResponseRedirect(reverse_lazy("home"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse_lazy("home"))


def render_login_form(request):
    invalid_form = False

    login_form = TeacherLoginForm(prefix="login")

    school_login_form = StudentLoginForm(prefix="login")

    independent_student_login_form = IndependentStudentLoginForm(
        prefix="independent_student"
    )
    independent_student_view = False

    render_dict = {
        "login_form": login_form,
        "school_login_form": school_login_form,
        "independent_student_login_form": independent_student_login_form,
        "independent_student_view": independent_student_view,
        "logged_in_as_teacher": is_logged_in_as_teacher(request),
        "settings": app_settings,
    }

    if request.method == "POST":
        form, process_form, render_dict = configure_post_login(request, render_dict)

        if form.is_valid():
            return process_form(request, form)
        else:
            invalid_form = True

    res = render(request, "portal/login.html", render_dict)

    res.count = invalid_form
    return res


def configure_post_login(request, render_dict):
    if "login-access_code" in request.POST:
        form = StudentLoginForm(request.POST, prefix="login")
        process_form = process_student_login_form
        render_dict["school_login_form"] = form
    elif "independent_student-username" in request.POST:
        form = IndependentStudentLoginForm(request.POST, prefix="independent_student")
        process_form = process_indep_student_login_form
        render_dict["independent_student_login_form"] = form
        render_dict["independent_student_view"] = True
    else:
        form = TeacherLoginForm(request.POST, prefix="login")
        process_form = process_login_form
        render_dict["login_form"] = form

    return form, process_form, render_dict


def render_signup_form(request):
    invalid_form = False

    teacher_signup_form = TeacherSignupForm(prefix="teacher_signup")
    independent_student_signup_form = IndependentStudentSignupForm(
        prefix="independent_student_signup"
    )

    if request.method == "POST":
        if "teacher_signup-teacher_email" in request.POST:
            teacher_signup_form = TeacherSignupForm(
                request.POST, prefix="teacher_signup"
            )

            if not captcha.CAPTCHA_ENABLED:
                remove_captcha_from_forms(teacher_signup_form)

            if teacher_signup_form.is_valid():
                data = teacher_signup_form.cleaned_data
                return process_signup_form(request, data)

        else:
            independent_student_signup_form = IndependentStudentSignupForm(
                request.POST, prefix="independent_student_signup"
            )

            if independent_student_signup_form.is_valid():
                data = independent_student_signup_form.cleaned_data
                return process_independent_student_signup_form(request, data)

    res = render(
        request,
        "portal/register.html",
        {
            "teacher_signup_form": teacher_signup_form,
            "independent_student_signup_form": independent_student_signup_form,
        },
    )

    res.count = invalid_form
    return res


def process_login_form(request, login_form):
    user = login_form.user
    if not is_verified(user):
        send_verification_email(request, user)
        return render(request, "portal/email_verification_needed.html", {"user": user})

    login(request, login_form.user)

    if using_two_factor(request.user):
        return render(
            request,
            "portal/2FA_redirect.html",
            {
                "form": AuthenticationForm(),
                "username": request.user.username,
                "password": login_form.cleaned_data["teacher_password"],
            },
        )

    next_url = request.GET.get("next", None)
    if next_url and is_safe_url(next_url):
        return HttpResponseRedirect(next_url)

    teacher = request.user.userprofile.teacher

    return redirect_teacher_to_correct_page(request, teacher)


def process_student_login_form(request, school_login_form):
    login(request, school_login_form.user)

    next_url = request.GET.get("next", None)
    if next_url and is_safe_url(next_url):
        return HttpResponseRedirect(next_url)

    student = request.user.userprofile.student
    student_class = student.class_field
    student_school = student_class.teacher.school

    messages.info(
        request,
        (
            "You are logged in as a member of class: <strong>"
            + escape(student_class.name)
            + "</strong>, in school or club: <strong>"
            + escape(student_school.name)
            + "</strong>."
        ),
        extra_tags="safe",
    )

    return HttpResponseRedirect(reverse_lazy("student_details"))


def process_indep_student_login_form(request, independent_student_login_form):
    user = independent_student_login_form.user
    if not is_verified(user):
        send_verification_email(request, user)
        return render(request, "portal/email_verification_needed.html", {"user": user})

    login(request, independent_student_login_form.user)

    next_url = request.GET.get("next", None)
    if next_url and is_safe_url(next_url):
        return HttpResponseRedirect(next_url)

    return HttpResponseRedirect(reverse_lazy("student_details"))


def _newsletter_ticked(form_data):
    return form_data["newsletter_ticked"]


def process_signup_form(request, data):
    email = data["teacher_email"]
    teacher = None

    if email and Teacher.objects.filter(new_user__email=email).exists():
        email_message = email_messages.userAlreadyRegisteredEmail(request, email)
        send_email(
            NOTIFICATION_EMAIL,
            [email],
            email_message["subject"],
            email_message["message"],
        )
    else:
        teacher = Teacher.objects.factory(
            title=data["teacher_title"],
            first_name=data["teacher_first_name"],
            last_name=data["teacher_last_name"],
            email=data["teacher_email"],
            password=data["teacher_password"],
        )

        if _newsletter_ticked(data):
            user = teacher.user.user
            add_to_dotmailer(user.first_name, user.last_name, user.email)

        send_verification_email(request, teacher.user.user)

    if teacher:
        return render(
            request,
            "portal/email_verification_needed.html",
            {"user": teacher.user.user},
        )
    else:
        return render(request, "portal/email_verification_needed.html")


def process_independent_student_signup_form(request, data):
    email = data["email"]
    username = data["username"]

    independent_students = Student.objects.filter(class_field=None)

    if is_independent_email_already_used(email, independent_students):
        email_message = email_messages.userAlreadyRegisteredEmail(request, email)
        send_email(
            NOTIFICATION_EMAIL,
            [email],
            email_message["subject"],
            email_message["message"],
        )
        return render(request, "portal/email_verification_needed.html")

    if is_independent_username_already_used(username, independent_students):
        email_message = email_messages.indepStudentUsernameAlreadyExistsEmail(
            request, username
        )
        send_email(
            NOTIFICATION_EMAIL,
            [email],
            email_message["subject"],
            email_message["message"],
        )
        return render(request, "portal/email_verification_needed.html")

    student = Student.objects.independentStudentFactory(
        username=data["username"],
        name=data["name"],
        email=data["email"],
        password=data["password"],
    )

    if _newsletter_ticked(data):
        user = student.new_user
        add_to_dotmailer(user.first_name, user.last_name, user.email)

    send_verification_email(request, student.new_user)

    return render(
        request, "portal/email_verification_needed.html", {"user": student.new_user}
    )


def is_independent_email_already_used(email, independent_students):
    return email and independent_students.filter(new_user__email=email).exists()


def is_independent_username_already_used(username, independent_students):
    return (
        username and independent_students.filter(new_user__username=username).exists()
    )


def is_logged_in_as_teacher(request):
    logged_in_as_teacher = (
        hasattr(request.user, "userprofile")
        and hasattr(request.user.userprofile, "teacher")
        and (request.user.is_verified() or not using_two_factor(request.user))
    )
    return logged_in_as_teacher


def is_developer(request):
    return hasattr(request.user, "userprofile") and request.user.userprofile.developer


def is_logged_in_as_student(request):
    is_student = hasattr(request.user, "userprofile") and hasattr(
        request.user.userprofile, "student"
    )
    return (
        request.user.is_verified() or not using_two_factor(request.user) and is_student
    )


def redirect_teacher_to_correct_page(request, teacher):
    if teacher.has_school():
        classes = teacher.class_teacher.all()
        if classes:
            classes_count = classes.count()
            if classes_count > 1 or classes[0].has_students():
                link = reverse("two_factor:profile")
                messages.info(
                    request,
                    (
                        "You are not currently set up with two-factor authentication. "
                        + "Use your phone or tablet to enhance your account’s security.</br>"
                        + "Click <a href='"
                        + link
                        + "'>here</a> to find out more and "
                        + "set it up or go to your account page at any time."
                    ),
                    extra_tags="safe",
                )
                return HttpResponseRedirect(reverse_lazy("dashboard"))
            else:
                return HttpResponseRedirect(
                    reverse_lazy(
                        "onboarding-class",
                        kwargs={"access_code": classes[0].access_code},
                    )
                )
        else:
            return HttpResponseRedirect(reverse_lazy("onboarding-classes"))
    else:
        return HttpResponseRedirect(reverse_lazy("onboarding-organisation"))


@csrf_exempt
def process_newsletter_form(request):
    if request.method == "POST":
        newsletter_form = NewsletterForm(data=request.POST)
        if newsletter_form.is_valid():
            user_email = newsletter_form.cleaned_data["email"]
            add_to_dotmailer("", "", user_email)
            messages.success(request, "Thank you for signing up! 🎉")
            return HttpResponseRedirect(reverse_lazy("home"))
        messages.error(
            request,
            "Invalid email address. Please try again.",
            extra_tags="sub-nav--warning",
        )
        return HttpResponseRedirect(reverse_lazy("home"))

    return HttpResponse(status=405)


@cache_control(private=True)
def home(request):
    link = reverse("home-learning")
    messages.success(
        request,
        "<a href='"
        + link
        + "'>Download</a> your FREE parent packs today and help your children learn coding skills through play.",
        extra_tags="safe",
    )

    return render(request, "portal/home.html")


def home_learning(request):
    return render(
        request,
        "portal/home_learning.html",
        {"HOME_LEARNING_BANNER": HOME_LEARNING_BANNER},
    )
