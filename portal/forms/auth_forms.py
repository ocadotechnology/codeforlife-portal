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
from django import forms
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth import forms as django_auth_forms
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from portal.models import Student, Teacher
import password_strength_test


class PasswordResetSetPasswordForm(django_auth_forms.SetPasswordForm):
    def __init__(self, user, *args, **kwags):
        super(PasswordResetSetPasswordForm, self).__init__(user, *args, **kwags)
        self.fields['new_password1'].label = "Enter your new password"
        self.fields['new_password1'].widget.attrs['placeholder'] = "Enter your new password"
        self.fields['new_password2'].label = "Confirm your new password"
        self.fields['new_password2'].widget.attrs['placeholder'] = "Confirm your new password"

    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1', None)
        if hasattr(self.user.userprofile, 'teacher'):
            if not password_strength_test(new_password1):
                raise forms.ValidationError(
                    "Password not strong enough, consider using at least 8 characters, upper and "
                    + "lower case letters, and numbers")
        elif hasattr(self.user.userprofile, 'student'):
            if not password_strength_test(new_password1, length=6, upper=False, lower=False,
                                          numbers=False):
                raise forms.ValidationError(
                    "Password not strong enough, consider using at least 6 characters")
        return new_password1
