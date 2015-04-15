from functools import partial

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.http import urlsafe_base64_decode
from django.core.urlresolvers import reverse_lazy
from django.contrib import messages as messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.views import password_reset, password_reset_confirm
from django.contrib.auth import get_user_model
from two_factor.views import LoginView
from recaptcha import RecaptchaClient
from django_recaptcha_field import create_form_subclass_with_recaptcha

from portal.models import UserProfile, Teacher, Class, Student
from portal.forms.registration import PasswordResetSetPasswordForm, StudentPasswordResetForm, TeacherPasswordResetForm
from portal.permissions import not_logged_in
from portal.helpers.email import PASSWORD_RESET_EMAIL
from ratelimit.decorators import ratelimit

recaptcha_client = RecaptchaClient(settings.RECAPTCHA_PRIVATE_KEY, settings.RECAPTCHA_PUBLIC_KEY)

@ratelimit('def', periods=['1m'])
def custom_2FA_login(request):
    block_limit = 5

    if getattr(request, 'limits', { 'def' : [0] })['def'][0] >= block_limit:
        return HttpResponseRedirect(reverse_lazy('locked_out'))

    return LoginView.as_view()(request)

@user_passes_test(not_logged_in, login_url=reverse_lazy('current_user'))
def password_reset_check_and_confirm(request, uidb64=None, token=None, post_reset_redirect=None):
    # Customised standard django auth view with customised form to incorporate checking the password set is strong enough
    UserModel = get_user_model()
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None
    if user != None:
        if hasattr(user.userprofile, 'student'):
            usertype = 'STUDENT'
        elif hasattr(user.userprofile, 'teacher'):
            usertype = 'TEACHER'
    return password_reset_confirm(request, set_password_form=PasswordResetSetPasswordForm, uidb64=uidb64, token=token, post_reset_redirect=post_reset_redirect, extra_context= { 'usertype': usertype })

@user_passes_test(not_logged_in, login_url=reverse_lazy('current_user'))
def student_password_reset(request, post_reset_redirect):
    return password_reset(request, from_email=PASSWORD_RESET_EMAIL, template_name='registration/student_password_reset_form.html', password_reset_form=StudentPasswordResetForm, post_reset_redirect=post_reset_redirect)

@user_passes_test(not_logged_in, login_url=reverse_lazy('current_user'))
def teacher_password_reset(request, post_reset_redirect):
    return password_reset(request, from_email=PASSWORD_RESET_EMAIL, template_name='registration/teacher_password_reset_form.html', password_reset_form=TeacherPasswordResetForm, post_reset_redirect=post_reset_redirect)
