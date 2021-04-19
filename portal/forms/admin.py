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
import re

from django import forms
from django.contrib.auth.forms import (
    PasswordChangeForm,
    UserCreationForm,
    AdminPasswordChangeForm,
)

ADMIN_PASSWORD_TOO_WEAK_MESSAGE = """
Password is too weak. Please choose a password that's at least 14 characters long,
contains at least one lowercase letter, one uppercase letter, one digit and
one special character.
"""

ADMIN_PASSWORD_PATTERN = re.compile(
    "^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{14,}$"
)


class AdminChangeOwnPasswordForm(PasswordChangeForm):
    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_too_weak": ADMIN_PASSWORD_TOO_WEAK_MESSAGE,
    }

    def clean_new_password1(self):
        new_password1 = self.cleaned_data["new_password1"]

        if not re.match(ADMIN_PASSWORD_PATTERN, new_password1):
            raise forms.ValidationError(
                self.error_messages["password_too_weak"],
                code="password_too_weak",
            )

        return new_password1


class AdminUserCreationForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        "password_too_weak": ADMIN_PASSWORD_TOO_WEAK_MESSAGE,
    }

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]

        if not re.match(ADMIN_PASSWORD_PATTERN, password1):
            raise forms.ValidationError(
                self.error_messages["password_too_weak"],
                code="password_too_weak",
            )

        return password1


class AdminChangeUserPasswordForm(AdminPasswordChangeForm):
    error_messages = {
        **AdminPasswordChangeForm.error_messages,
        "password_too_weak": ADMIN_PASSWORD_TOO_WEAK_MESSAGE,
    }

    def clean_password1(self):
        password1 = self.cleaned_data["password1"]

        if not re.match(ADMIN_PASSWORD_PATTERN, password1):
            raise forms.ValidationError(
                self.error_messages["password_too_weak"],
                code="password_too_weak",
            )

        return password1
