import logging
import math

from common.helpers.emails import (
    send_verification_email,
)
from common.mail import campaign_ids, send_dotdigital_email
from common.models import DynamicElement, Student, Teacher, TotalActivity
from common.permissions import logged_in_as_student, logged_in_as_teacher
from common.utils import _using_two_factor
from django.contrib import messages as messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.html import format_html
from django.views.decorators.cache import cache_control

from deploy import captcha
from portal.forms.play import IndependentStudentSignupForm
from portal.forms.teach import TeacherSignupForm
from portal.helpers.captcha import remove_captcha_from_forms
from portal.helpers.ratelimit import (
    RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_GROUP,
    RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_RATE,
    is_ratelimited,
)
from portal.strings.coding_club import CODING_CLUB_BANNER
from portal.strings.home_learning import HOME_LEARNING_BANNER
from portal.strings.ten_year_map import (
    TEN_YEAR_MAP_BANNER,
    TEN_YEAR_MAP_HEADLINE,
)

LOGGER = logging.getLogger(__name__)


def register_view(request):
    if request.user.is_authenticated:
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


def _newsletter_ticked(form_data):
    return form_data["newsletter_ticked"]


def process_signup_form(request, data):
    email = data["teacher_email"]

    if email and User.objects.filter(email=email).exists():

        is_email_ratelimited = is_ratelimited(
            request=request,
            group=RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_GROUP,
            key=lambda *_: email,
            rate=RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_RATE,
            increment=True,
        )

        if not is_email_ratelimited:
            send_dotdigital_email(
                campaign_ids["user_already_registered"],
                [email],
                personalization_values={
                    "EMAIL": email,
                    "LOGIN_URL": request.build_absolute_uri(
                        reverse("teacher_login")
                    ),
                },
            )
        else:
            LOGGER.warn(
                f"Ratelimit teacher {RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_GROUP}: {email}"
            )
    else:
        teacher = Teacher.objects.factory(
            first_name=data["teacher_first_name"],
            last_name=data["teacher_last_name"],
            email=data["teacher_email"],
            password=data["teacher_password"],
        )

        send_verification_email(request, teacher.user.user, data)

        TotalActivity.objects.update(
            teacher_registrations=F("teacher_registrations") + 1
        )

    return render(
        request,
        "portal/email_verification_needed.html",
        {"usertype": "TEACHER"},
        status=302,
    )


def process_independent_student_signup_form(request, data):
    email = data["email"]

    if email and User.objects.filter(email=email).exists():
        is_email_ratelimited = is_ratelimited(
            request=request,
            group=RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_GROUP,
            key=lambda *_: email,
            rate=RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_RATE,
            increment=True,
        )

        if not is_email_ratelimited:
            send_dotdigital_email(
                campaign_ids["user_already_registered"],
                [email],
                personalization_values={
                    "EMAIL": email,
                    "LOGIN_URL": request.build_absolute_uri(
                        reverse("independent_student_login")
                    ),
                },
            )
        else:
            LOGGER.warning(
                f"Ratelimit independent {RATELIMIT_USER_ALREADY_REGISTERED_EMAIL_GROUP}: {email}"
            )
        return render(
            request,
            "portal/email_verification_needed.html",
            {"usertype": "INDEP_STUDENT"},
            status=302,
        )

    student = Student.objects.independentStudentFactory(
        name=data["name"], email=data["email"], password=data["password"]
    )

    dob = data["date_of_birth"]
    age_in_days = timezone.now().date() - dob
    age = math.floor(age_in_days.days / 365.25)

    send_verification_email(request, student.new_user, data, age=age)

    TotalActivity.objects.update(
        independent_registrations=F("independent_registrations") + 1
    )

    return render(
        request,
        "portal/email_verification_needed.html",
        {"usertype": "INDEP_STUDENT"},
        status=302,
    )


def is_developer(request):
    return (
        hasattr(request.user, "userprofile")
        and request.user.userprofile.developer
    )


def redirect_teacher_to_correct_page(request, teacher):
    if teacher.has_school():
        link = reverse("two_factor:profile")
        if not _using_two_factor(request.user):
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
        return reverse_lazy("dashboard")
    else:
        return reverse_lazy("onboarding-organisation")


@cache_control(private=True)
def home(request):
    # Putting this in a try catch because it causes some weird issue in the
    # tests where the first Selenium test passes, but any following test
    # fails because it cannot find the Maintenance banner instance.
    try:
        maintenance_banner = DynamicElement.objects.get(
            name="Maintenance banner"
        )

        if maintenance_banner.active:
            messages.info(
                request, format_html(maintenance_banner.text), extra_tags="safe"
            )
    except ObjectDoesNotExist:
        pass

    """
    This view is where we can add any messages to be shown upon loading the home page.
    Following this format:

    messages.success(request, "message text here", extra_tags="tag classes here")

    This example uses the success function which will display a welcoming message on the
    sub banner (right under the page header). Other functions can be used to indicate a
    warning, an error or a simple information.
    """
    return render(request, "portal/home.html")


def coding_club(request):
    return render(
        request, "portal/coding_club.html", {"BANNER": CODING_CLUB_BANNER}
    )


def home_learning(request):
    return render(
        request,
        "portal/home_learning.html",
        {"HOME_LEARNING_BANNER": HOME_LEARNING_BANNER},
    )


def ten_year_map_page(request):
    messages.info(
        request, "This page is currently under construction.", extra_tags="safe"
    )
    return render(
        request,
        "portal/ten_year_map.html",
        {"BANNER": TEN_YEAR_MAP_BANNER, "HEADLINE": TEN_YEAR_MAP_HEADLINE},
    )


def reset_screentime_warning(request):
    if request.user.is_authenticated:
        request.session["last_screentime_warning"] = timezone.now().timestamp()
    return HttpResponse(status=204)  # No content
