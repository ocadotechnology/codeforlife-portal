# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
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
from uuid import uuid4
import random
import string

from django.contrib.auth.models import User

from portal.models import Student, Class


def get_random_username():
    while True:
        random_username = uuid4().hex[:30]  # generate a random username
        if not User.objects.filter(username=random_username).exists():
            return random_username


def generate_new_student_name(orig_name):
    if not Student.objects.filter(user__user__username=orig_name).exists():
        return orig_name

    i = 1
    while True:
        new_name = orig_name + unicode(i)
        if not Student.objects.filter(user__user__username=new_name).exists():
            return new_name
        i += 1


def generate_access_code():
    while True:
        first_part = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
        second_part = ''.join(random.choice(string.digits) for _ in range(3))
        access_code = first_part + second_part

        if not Class.objects.filter(access_code=access_code).exists():
            return access_code


def generate_password(length):
    chars = set(string.ascii_lowercase + string.digits)
    chars.remove('l')
    chars.remove('0')
    return ''.join(random.choice(list(chars)) for _ in range(length))
