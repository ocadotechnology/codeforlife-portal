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
import re

from portal.models import Teacher, Class
from portal.helpers.generators import generate_access_code


def generate_details():
    name = "Class %d" % generate_details.next_id
    accesss_code = generate_access_code()

    generate_details.next_id += 1

    return name, accesss_code


generate_details.next_id = 1


def create_class_directly(teacher_email, class_name=None):
    name, accesss_code = generate_details()

    if class_name is not None:
        name = class_name

    teacher = Teacher.objects.get(new_user__email=teacher_email)

    klass = Class.objects.create(name=name, access_code=accesss_code, teacher=teacher)

    return klass, name, accesss_code


def create_class(page):
    name, _ = generate_details()

    page = page.create_class(name, "False")

    return page, name


def transfer_class(page, teacher_index):
    return page.transfer_class().select_teacher_by_index(teacher_index).move()
