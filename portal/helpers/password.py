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
from django.contrib.auth import update_session_auth_hash

import re

MINIMUM_PASSWORD_LENGTH = 8


def password_strength_test(password, upper=True, lower=True, numbers=True):
    most_used_passwords_2018 = ["Abcd1234", "Password1", "Qwerty123"]
    return (
        len(password) >= MINIMUM_PASSWORD_LENGTH
        and (not upper or re.search(r"[A-Z]", password))
        and (not lower or re.search(r"[a-z]", password))
        and (not numbers or re.search(r"[0-9]", password))
        and (password not in most_used_passwords_2018)
    )


def form_clean_password(self, forms, password_field_name):
    password = self.cleaned_data.get(password_field_name, None)

    if password and not password_strength_test(password):
        raise forms.ValidationError(
            "Password not strong enough, consider using at least {} characters, upper "
            "and lower case letters, and numbers.".format(MINIMUM_PASSWORD_LENGTH)
        )

    return password


def check_update_password(form, user, request, data):
    if data["password"] != "":
        user.set_password(data["password"])
        user.save()
        update_session_auth_hash(request, form.user)
