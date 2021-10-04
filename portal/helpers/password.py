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
from enum import Enum, auto

from django import forms
from django.contrib.auth import update_session_auth_hash


class PasswordStrength(Enum):
    STUDENT = auto()
    INDEPENDENT = auto()
    TEACHER = auto()

    def password_test(self, password):
        if self is PasswordStrength.STUDENT:
            minimum_password_length = 6
            # Make student password case insensitive
            password = password.lower()
            if password and not password_strength_test(
                password=password,
                minimum_password_length=minimum_password_length,
                upper=False,
                lower=False,
                numbers=False,
                special_char=False,
            ):
                raise forms.ValidationError(
                    f"Password not strong enough, consider using at least {minimum_password_length} characters."
                )
        elif self is PasswordStrength.INDEPENDENT:
            minimum_password_length = 8
            if password and not password_strength_test(
                password=password,
                minimum_password_length=minimum_password_length,
                upper=True,
                lower=True,
                numbers=True,
                special_char=False,
            ):
                raise forms.ValidationError(
                    f"Password not strong enough, consider using at least {minimum_password_length} characters, "
                    "upper and lower case letters, and numbers."
                )
        else:
            minimum_password_length = 10
            if password and not password_strength_test(
                password=password,
                minimum_password_length=minimum_password_length,
                upper=True,
                lower=True,
                numbers=True,
                special_char=True,
            ):
                raise forms.ValidationError(
                    f"Password not strong enough, consider using at least {minimum_password_length} characters, "
                    "upper and lower case letters, numbers and special characters."
                )
        return password


def password_strength_test(
    password,
    minimum_password_length,
    upper=True,
    lower=True,
    numbers=True,
    special_char=True,
):
    most_used_passwords = [
        "Abcd1234",
        "Password1",
        "Qwerty123",
        "password",
        "qwerty",
        "abcdef",
    ]
    return (
        len(password) >= minimum_password_length
        and (not upper or re.search(r"[A-Z]", password))
        and (not lower or re.search(r"[a-z]", password))
        and (not numbers or re.search(r"[0-9]", password))
        and (
            not special_char
            or re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password)
        )
        and (password not in most_used_passwords)
    )


def form_clean_password(self, password_field_name, strength: PasswordStrength):
    password = self.cleaned_data.get(password_field_name, None)
    password = strength.password_test(password)
    return password


def check_update_password(form, user, request, data):
    changing_password = False
    if data["password"] != "":
        changing_password = True
        user.set_password(data["password"])
        user.save()
        update_session_auth_hash(request, form.user)

    return changing_password
