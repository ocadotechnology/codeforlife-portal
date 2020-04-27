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
from builtins import object
from django import forms

from portal.models import School

from django_countries.widgets import CountrySelectWidget
from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import EmailValidator


class OrganisationForm(forms.ModelForm):
    class Meta(object):

        model = School
        fields = ["name", "postcode", "country"]
        labels = {
            "name": "Name of your school or club",
            "postcode": "Postcode",
            "country": "Country",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "placeholder": "Name of your school or club",
                }
            ),
            "postcode": forms.TextInput(
                attrs={"autocomplete": "off", "placeholder": "Postcode"}
            ),
            "country": CountrySelectWidget(attrs={"class": "wide"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.current_school = kwargs.pop("current_school", None)
        super(OrganisationForm, self).__init__(*args, **kwargs)
        self.fields["postcode"].strip = False

    def clean(self):
        name = self.cleaned_data.get("name", None)
        postcode = self.cleaned_data.get("postcode", None)

        if name and postcode:
            try:
                school = School.objects.get(name=name, postcode=postcode)
            except ObjectDoesNotExist:
                return self.cleaned_data

            if not self.current_school or self.current_school.id != school.id:
                raise forms.ValidationError(
                    "There is already a school or club registered with that name and postcode"
                )

        return self.cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get("name", None)
        validator = EmailValidator()

        if name:
            try:
                validator(name)
                is_email = True
            except forms.ValidationError:
                is_email = False

            if is_email:
                raise forms.ValidationError(
                    "Please make sure your organisation name is valid"
                )

        return name

    def clean_postcode(self):
        postcode = self.cleaned_data.get("postcode", None)

        if postcode:
            if (
                len(postcode.replace(" ", "")) > 10
                or len(postcode.replace(" ", "")) == 0
            ):
                raise forms.ValidationError("Please enter a valid postcode or ZIP code")

        return postcode


class OrganisationJoinForm(forms.Form):
    fuzzy_name = forms.CharField(
        label="Search for school or club by name or postcode",
        widget=forms.TextInput(attrs={"placeholder": "Enrico Fermi High School"}),
    )

    # Note: the reason this is a CharField rather than a ChoiceField is to avoid having to
    # provide choices which was problematic given that the options are dynamically generated.
    chosen_org = forms.CharField(
        label="Select school or club", widget=forms.Select(attrs={"class": "wide"})
    )

    def clean_chosen_org(self):
        chosen_org = self.cleaned_data.get("chosen_org", None)

        if chosen_org and not School.objects.filter(id=int(chosen_org)).exists():
            raise forms.ValidationError("That school or club was not recognised")

        return chosen_org
