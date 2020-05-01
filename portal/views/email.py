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
from datetime import timedelta

from django.contrib import messages as messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse_lazy
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django_countries import countries

from portal.app_settings import CONTACT_FORM_EMAILS
from portal.helpers.emails import NOTIFICATION_EMAIL, send_email
from portal.models import EmailVerification, School, Student, Teacher
from portal.permissions import logged_in_as_independent_student


def verify_email(request, token):
    verifications = EmailVerification.objects.filter(token=token)

    if has_verification_failed(verifications):
        return render(request, "portal/email_verification_failed.html")

    verification = verifications[0]

    verification.verified = True
    verification.save()

    user = verification.user

    if verification.email:  # verifying change of email address
        user.email = verification.email
        user.save()

        user.email_verifications.exclude(email=user.email).delete()

    messages.success(
        request, "Your email address was successfully verified, please log in."
    )

    if logged_in_as_independent_student(user):
        login_url = "independent_student_login"
    else:
        login_url = "teacher_login"

    return HttpResponseRedirect(reverse_lazy(login_url))


def has_verification_failed(verifications):
    return (
        len(verifications) != 1
        or verifications[0].verified
        or (verifications[0].expiry - timezone.now()) < timedelta()
    )


def send_new_users_report(request):
    new_users_count = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    users_count = User.objects.count()
    active_users = User.objects.filter(
        last_login__gte=timezone.now() - timedelta(days=7)
    ).count()
    school_count = School.objects.count()
    teacher_count = Teacher.objects.count()
    student_count = Student.objects.count()
    schools_countries = (
        School.objects.values("country")
        .annotate(nb_countries=Count("id"))
        .order_by("-nb_countries")
    )
    nb_countries = schools_countries.count()
    countries_count = "\n".join(
        "{}: {}".format(dict(countries)[k["country"]], k["nb_countries"])
        for k in schools_countries[:3]
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
    )
    return HttpResponse("success")
