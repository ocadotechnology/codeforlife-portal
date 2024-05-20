from datetime import timedelta

import jwt
from common.models import Teacher
from common.permissions import logged_in_as_independent_student
from django.conf import settings
from django.contrib import messages as messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone


def verify_email(request, token):
    decoded_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    user_found = User.objects.filter(email=decoded_jwt["email"]).first()
    usertype = (
        "TEACHER"
        if Teacher.objects.filter(new_user=user_found).exists()
        else "INDEP_STUDENT"
    )
    is_expired = decoded_jwt["expires"] < timezone.now().timestamp()

    is_changing_email = decoded_jwt["new_email"] != ""
    updated_email = (
        decoded_jwt["new_email"] if is_changing_email else decoded_jwt["email"]
    )

    if not user_found or is_expired:
        return render(
            request,
            "portal/email_verification_failed.html",
            {"usertype": usertype},
        )

    is_user_verified = user_found.userprofile.is_verified
    if is_user_verified and not is_changing_email:
        return render(
            request,
            "portal/email_verification_failed.html",
            {"usertype": usertype},
        )

    if not is_user_verified or is_changing_email:
        user_found.email = updated_email
        user_found.username = updated_email
        user_found.userprofile.is_verified = True
        user_found.userprofile.save()
        user_found.save()

    messages.success(
        request, "Your email address was successfully verified, please log in."
    )

    if logged_in_as_independent_student(user_found):
        login_url = "independent_student_login"
    else:
        login_url = "teacher_login"

    return HttpResponseRedirect(reverse_lazy(login_url))


def has_verification_failed(verifications):
    return (
        len(verifications) > 1
        or verifications[0].verified
        or (verifications[0].expiry - timezone.now()) < timedelta()
    )
