# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2021, Ocado Innovation Limited
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

import random
import sys

from common.helpers.emails import generate_token
from common.models import Teacher
from django.core import mail

from . import email


def generate_details(**kwargs):
    random_int = random.randint(1, sys.maxsize)
    title = kwargs.get("title", "Mr")
    first_name = kwargs.get("first_name", "Test")
    last_name = kwargs.get("last_name", f"Teacher {random_int}")
    email_address = kwargs.get(
        "email_address",
        f"testteacher{random_int}@codeforlife.com",
    )
    password = kwargs.get("password", "Password2")

    return title, first_name, last_name, email_address, password


def signup_teacher_directly(preverified=True, **kwargs):
    """
    Creates a Teacher object by using the details passed in as kwargs, or by
    generating random details. Also verifies the teacher's email if preverified
    is True.
    :param preverified: whether or not the teacher's email should be verified.
    :return: the teacher's email and password.
    """
    title, first_name, last_name, email_address, password = generate_details(**kwargs)
    teacher = Teacher.objects.factory(
        title, first_name, last_name, email_address, password
    )
    generate_token(teacher.new_user, preverified=preverified)
    teacher.user.save()
    return email_address, password


def signup_duplicate_teacher_fail(page, duplicate_email):
    page = page.go_to_signup_page()

    title, first_name, last_name, email_address, password = generate_details()
    page = page.signup(
        title, first_name, last_name, duplicate_email, password, password
    )

    page = page.return_to_home_page()

    page = email.follow_duplicate_account_link_to_login(page, mail.outbox[0], "teacher")
    mail.outbox = []

    return page, email_address, password


def signup_teacher(page, newsletter=False):
    page = page.go_to_signup_page()

    title, first_name, last_name, email_address, password = generate_details()
    page = page.signup(
        title,
        first_name,
        last_name,
        email_address,
        password=password,
        confirm_password=password,
        newsletter=newsletter,
    )

    page = page.return_to_home_page()

    page = email.follow_verify_email_link_to_onboarding(page, mail.outbox[0])
    mail.outbox = []

    return page, email_address, password


def verify_email(page):
    assert len(mail.outbox) > 0

    page = email.follow_verify_email_link_to_login(page, mail.outbox[0], "teacher")
    mail.outbox = []

    return page


def submit_teacher_signup_form(page, password="test"):
    page = page.go_to_signup_page()

    title, first_name, last_name, email_address, _ = generate_details()
    return page.signup(
        title,
        first_name,
        last_name,
        email_address,
        password=password,
        confirm_password=password,
        success=False,
        newsletter=True,
    )
