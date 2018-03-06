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
from django import forms
from portal.helpers.regex import get_regex_name, get_regex_message, get_regex_telephone
from captcha.fields import ReCaptchaField


class ContactForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100,
                           widget=forms.TextInput(attrs={'class': 'contactField'}))
    telephone = forms.CharField(label='Telephone', max_length=50,
                                widget=forms.TextInput(attrs={'class': 'contactField'}))
    email = forms.EmailField(label='Email address',
                             widget=forms.EmailInput(attrs={'class': 'contactField'}))
    message = forms.CharField(label='Message', max_length=250,
                              widget=forms.Textarea(attrs={'class': 'contactField'}))
    browser = forms.CharField(label='Browser', max_length=250, required=False,
                              widget=forms.TextInput(attrs={'type': 'hidden', 'id': 'browserField'}))

    captcha = ReCaptchaField()

    def clean_name(self):
        name = self.cleaned_data.get("name", None)

        if get_regex_name().match(name) is None:
            raise forms.ValidationError("Names may only contain letters, numbers, dashes, underscores, and spaces.")

        return name

    def clean_message(self):
        message = self.cleaned_data.get("message", None)
        line_list = message.splitlines()

        for line in line_list:
            if get_regex_message().match(line) is None:
                raise forms.ValidationError("Your message may not contain special characters.")

        return message

    def clean_telephone(self):
        telephone = self.cleaned_data.get("telephone", None)

        if get_regex_telephone().match(telephone) is None:
            raise forms.ValidationError("Invalid phone number")

        return telephone
