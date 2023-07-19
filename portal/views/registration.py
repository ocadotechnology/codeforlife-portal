import ast
import re

from common.email_messages import accountDeletionEmail
from portal.views.login import has_user_lockout_expired

from django.contrib.auth.models import User
from datetime import datetime
from common.helpers.emails import (
    delete_contact,
    NOTIFICATION_EMAIL,
    PASSWORD_RESET_EMAIL,
    send_email,
)
from common.models import Teacher, Student, DailyActivity
from common.permissions import not_logged_in, not_fully_logged_in

from django.contrib import messages as messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST

from deploy import captcha
from portal import app_settings
from portal.forms.registration import (
    TeacherPasswordResetForm,
    TeacherPasswordResetSetPasswordForm,
    StudentPasswordResetForm,
    StudentPasswordResetSetPasswordForm,
)
from portal.helpers.captcha import remove_captcha_from_form
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user
from portal.views.api import anonymise


@user_passes_test(not_logged_in, login_url=reverse_lazy("home"))
def student_password_reset(request):
    usertype = "INDEP_STUDENT"
    return password_reset(
        request,
        usertype,
        from_email=PASSWORD_RESET_EMAIL,
        template_name="portal/reset_password.html",
        password_reset_form=StudentPasswordResetForm,
    )


def blocked_and_not_expired(user: Student or Teacher):
    return user.blocked_time and not has_user_lockout_expired(user)


def school_student_reset_password_tracker(request, activity_today):
    if "transfer_students" in request.POST:
        student_list = ast.literal_eval(request.POST.get("transfer_students", []))
        for student_id in student_list:
            current_student = Student.objects.get(id=student_id)
            if blocked_and_not_expired(current_student):
                activity_today.school_student_lockout_resets += 1
    elif "set_password" in request.POST:
        student_id = re.search("/(\d+)/", request.path).group(1)
        current_student = Student.objects.get(id=student_id)
        if blocked_and_not_expired(current_student):
            activity_today.school_student_lockout_resets += 1
    activity_today.save()


def teacher_or_indy_reset_password_tracker(request, activity_today, email):
    get_user = Teacher.objects.filter(new_user__email=email) or Student.objects.filter(new_user__email=email)
    if get_user.exists():
        user = get_user[0]
        if blocked_and_not_expired(user):
            if "teacher" in request.path:
                activity_today.teacher_lockout_resets += 1
            elif "student" in request.path:
                activity_today.indy_lockout_resets += 1
            activity_today.save()


def handle_reset_password_tracking(request, user_type, access_code=None, student_id=None):
    activity_today = DailyActivity.objects.get_or_create(date=datetime.now().date())[0]
    # school student has 2 different ways of resetting password
    # hence the function is extended
    # check for indy student or teacher account
    if user_type == "SCHOOL_STUDENT":
        school_student_reset_password_tracker(request, activity_today)
    elif "email" in request.POST:
        teacher_or_indy_reset_password_tracker(request, activity_today, request.POST.get("email", ""))


@user_passes_test(not_fully_logged_in, login_url=reverse_lazy("teacher_login"))
def teacher_password_reset(request):
    usertype = "TEACHER"
    return password_reset(
        request,
        usertype,
        from_email=PASSWORD_RESET_EMAIL,
        template_name="portal/reset_password.html",
        password_reset_form=TeacherPasswordResetForm,
    )


@csrf_protect
def password_reset(
    request,
    usertype,
    template_name="portal/reset_password.html",
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
        handle_reset_password_tracking(request, usertype)
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

            return render(request, "portal/reset_password_email_sent.html", {"usertype": usertype})
    else:
        form = password_reset_form()

    if not captcha.CAPTCHA_ENABLED:
        remove_captcha_from_form(form)

    context = {
        "form": form,
        "title": _("Password reset"),
        "settings": app_settings,
        "should_use_recaptcha": captcha.CAPTCHA_ENABLED,
        "usertype": usertype,
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

                return render(request, "portal/reset_password_done.html", {"usertype": usertype})
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = _("Password reset unsuccessful")

    context = {"form": form, "title": title, "validlink": validlink}

    update_context_and_apps(request, context, current_app, extra_context)

    return TemplateResponse(request, template_name, context)


def _check_and_unblock_user(username, usertype, access_code=None):
    if usertype == "TEACHER":
        user = Teacher.objects.get(new_user__username=username)
    elif usertype == "INDEP_STUDENT":
        user = Student.objects.get(new_user__username=username)
    elif usertype == "SCHOOL_STUDENT":
        user = Student.objects.get(new_user__first_name=username, class_field__access_code=access_code)

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
        usertype = "INDEP_STUDENT"
        return password_reset_confirm(
            request,
            usertype,
            set_password_form=StudentPasswordResetSetPasswordForm,
            uidb64=uidb64,
            token=token,
            extra_context={"usertype": usertype},
        )
    else:
        usertype = "TEACHER"
        return password_reset_confirm(
            request,
            usertype,
            set_password_form=TeacherPasswordResetSetPasswordForm,
            uidb64=uidb64,
            token=token,
            extra_context={"usertype": usertype},
        )


@require_POST
@login_required(login_url=reverse_lazy("teacher_login"))
def delete_account(request):
    user = request.user
    password = request.POST.get("password")

    if not user.check_password(password):
        messages.error(request, "Your account was not deleted due to incorrect password.")
        return HttpResponseRedirect(reverse_lazy("dashboard"))

    email = user.email
    anonymise(user)

    # remove from dotmailer
    if bool(request.POST.get("unsubscribe_newsletter")):
        delete_contact(email)

    # send confirmation email
    message = accountDeletionEmail(request)
    send_email(
        NOTIFICATION_EMAIL,
        [email],
        message["subject"],
        message["message"],
        message["title"],
    )

    return HttpResponseRedirect(reverse_lazy("home"))
