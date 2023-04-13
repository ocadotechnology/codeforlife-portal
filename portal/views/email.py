from datetime import timedelta

import jwt
from common.helpers.emails import NOTIFICATION_EMAIL, send_email
from common.models import School, Student, Teacher
from common.permissions import logged_in_as_independent_student
from django.conf import settings
from django.contrib import messages as messages
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django_countries import countries

from portal.app_settings import CONTACT_FORM_EMAILS


def verify_email(request, token):
    decoded_jwt = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

    user_found = User.objects.filter(email=decoded_jwt["email"]).first()
    usertype = "TEACHER" if Teacher.objects.filter(new_user=user_found).exists() else "INDEP_STUDENT"
    is_expired = decoded_jwt["expires"] < timezone.now().timestamp()

    is_changing_email = decoded_jwt["new_email"] != ""
    updated_email = decoded_jwt["new_email"] if is_changing_email else decoded_jwt["email"]

    if not user_found or is_expired:
        return render(request, "portal/email_verification_failed.html", {"usertype": usertype})

    is_user_verified = user_found.userprofile.is_verified
    if is_user_verified and not is_changing_email:
        return render(request, "portal/email_verification_failed.html", {"usertype": usertype})

    if not is_user_verified or is_changing_email:
        user_found.email = updated_email
        user_found.username = updated_email
        user_found.userprofile.is_verified = True
        user_found.userprofile.save()
        user_found.save()

    messages.success(request, "Your email address was successfully verified, please log in.")

    if logged_in_as_independent_student(user_found):
        login_url = "independent_student_login"
    else:
        login_url = "teacher_login"

    return HttpResponseRedirect(reverse_lazy(login_url))


def has_verification_failed(verifications):
    return (
        len(verifications) > 1 or verifications[0].verified or (verifications[0].expiry - timezone.now()) < timedelta()
    )


def send_new_users_report(request):
    new_users_count = User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=7)).count()
    users_count = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=7)).count()
    school_count = School.objects.count()
    teacher_count = Teacher.objects.count()
    student_count = Student.objects.count()
    schools_countries = School.objects.values("country").annotate(nb_countries=Count("id")).order_by("-nb_countries")
    nb_countries = schools_countries.count()
    countries_count = "\n".join(
        "{}: {}".format(dict(countries)[k["country"]], k["nb_countries"]) for k in schools_countries[:3]
    )
    send_email(
        NOTIFICATION_EMAIL,
        CONTACT_FORM_EMAILS,
        "new users",
        "There are {new_users} new users this week!\n"
        "The total number of registered users is now: {users}\n"
        "Current number of schools: {schools}\n"
        "Current number of teachers: {teachers}\n"
        "Current number of students: {students}\n"
        "Number of users that last logged in during the last week: {active_users}\n"
        "Number of countries with registered schools: {countries}\n"
        "Top 3 - schools per country:\n{countries_counter}".format(
            new_users=new_users_count,
            users=users_count,
            schools=school_count,
            teachers=teacher_count,
            students=student_count,
            countries=nb_countries,
            active_users=active_users,
            countries_counter=countries_count,
        ),
        "new users",
    )
    return HttpResponse("success")
