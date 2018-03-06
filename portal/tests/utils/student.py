# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
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
from django.core import mail

import email

from portal.models import Class, Student


def generate_school_details():
    name = 'Student %d' % generate_school_details.next_id
    password = 'Password1'

    generate_school_details.next_id += 1

    return name, password

generate_school_details.next_id = 1


def create_school_student_directly(access_code):
    name, password = generate_school_details()

    klass = Class.objects.get(access_code=access_code)
    student = Student.objects.schoolFactory(klass, name, password)

    return name, password, student


def create_school_student(page):
    name, _ = generate_school_details()

    page = page.type_student_name(name).create_students()

    return page, name


def create_many_school_students(page, n):
    names = ['' for i in range(n)]

    for i in range(n):
        names[i], _ = generate_school_details()
        page = page.type_student_name(names[i])

    page = page.create_students()

    return page, names


def generate_independent_student_details():
    name = 'Student %d' % generate_independent_student_details.next_id
    username = 'Student user %d' % generate_independent_student_details.next_id
    email_address = 'Student%d@codeforlife.com' % generate_independent_student_details.next_id
    password = 'Password1'

    generate_independent_student_details.next_id += 1

    return name, username, email_address, password

generate_independent_student_details.next_id = 1


def create_independent_student(page):
    page = page.go_to_signup_page()

    name, username, email_address, password = generate_independent_student_details()
    page = page.independent_student_signup(name, username, email_address, password, password)

    page = page.return_to_home_page()

    page = email.follow_verify_email_link_to_login(page, mail.outbox[0])
    mail.outbox = []

    return page, name, username, email_address, password


def submit_independent_student_signup_form(page, password='test'):
    page = page.go_to_signup_page()

    name, username, email_address, _ = generate_independent_student_details()
    return page.independent_student_signup(name, username, email_address, password, password, success=False)
