from common import email_messages
from common.helpers.emails import (
    send_verification_email,
    send_email,
    NOTIFICATION_EMAIL,
    add_to_dotmailer,
)
from common.models import Teacher, Student
from common.permissions import logged_in_as_student, logged_in_as_teacher
from django.contrib import messages as messages
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.decorators.cache import cache_control

from deploy import captcha
from portal.forms.play import IndependentStudentSignupForm
from portal.forms.teach import TeacherSignupForm
from portal.helpers.captcha import remove_captcha_from_forms
from portal.strings.home_learning import HOME_LEARNING_BANNER


def teach_email_labeller(request):
    if request.method == "POST" and "teacher_login" in request.POST:
        return request.POST["login-teacher_email"]

    return ""


def play_name_labeller(request):
    if request.method == "POST":
        if "school_login" in request.POST:
            return request.POST["login-name"] + ":" + request.POST["login-access_code"]

        if "independent_student_login" in request.POST:
            return request.POST["independent_student-username"]

    return ""


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
            first_name=data["teacher_first_name"],
            last_name=data["teacher_last_name"],
            email=data["teacher_email"],
            password=data["teacher_password"],
        )

        if _newsletter_ticked(data):
            user = teacher.user.user
            add_to_dotmailer(user.first_name, user.last_name, user.email)

        send_verification_email(request, teacher.user.user)

    return render(
        request,
        "portal/email_verification_needed.html",
        {"is_teacher": True},
    )


def process_independent_student_signup_form(request, data):
    email = data["email"]
    username = data["username"]

    independent_students = Student.objects.filter(class_field=None)

    if is_independent_email_already_used(email, independent_students):
        email_message = email_messages.userAlreadyRegisteredEmail(
            request, email, is_independent_student=True
        )
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
        request, "portal/email_verification_needed.html", {"is_teacher": False}
    )


def is_independent_email_already_used(email, independent_students):
    return email and independent_students.filter(new_user__email=email).exists()


def is_independent_username_already_used(username, independent_students):
    return (
        username and independent_students.filter(new_user__username=username).exists()
    )


def is_developer(request):
    return hasattr(request.user, "userprofile") and request.user.userprofile.developer


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
                return reverse_lazy("dashboard")
            else:
                return reverse_lazy(
                    "onboarding-class",
                    kwargs={"access_code": classes[0].access_code},
                )

        else:
            return reverse_lazy("onboarding-classes")
    else:
        return reverse_lazy("onboarding-organisation")


@cache_control(private=True)
def home(request):
    """
    This view is where we can add any messages to be shown upon loading the home page.
    Following this format:

    messages.success(request, "message text here", extra_tags="tag classes here")

    This example uses the success function which will display a welcoming message on the
    sub banner (right under the page header). Other functions can be used to indicate a
    warning, an error or a simple information.
    """
    return render(request, "portal/home.html")


def home_learning(request):
    return render(
        request,
        "portal/home_learning.html",
        {"HOME_LEARNING_BANNER": HOME_LEARNING_BANNER},
    )
