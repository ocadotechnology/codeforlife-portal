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
from datetime import timedelta
import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone

from portal.models import Student, Class, stripStudentName
from portal.helpers.password import password_strength_test
from captcha.fields import ReCaptchaField


class StudentLoginForm(forms.Form):
    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(attrs={'placeholder': "Jane"}))
    access_code = forms.CharField(
        label='Class Access Code',
        widget=forms.TextInput(attrs={'placeholder': "AB123"}))
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)

    captcha = ReCaptchaField()

    def clean(self):
        name = self.cleaned_data.get('name', None)
        access_code = self.cleaned_data.get('access_code', None)
        password = self.cleaned_data.get('password', None)

        if name and access_code and password:

            student, user = self.check_for_errors(name, access_code, password)

            self.student = student
            self.user = user

        return self.cleaned_data

    def check_for_errors(self, name, access_code, password):
        classes = Class.objects.filter(access_code__iexact=access_code)
        if len(classes) != 1:
            raise forms.ValidationError("Invalid name, class access code or password")

        name = stripStudentName(name)

        students = Student.objects.filter(new_user__first_name__iexact=name, class_field=classes[0])
        if len(students) != 1:
            raise forms.ValidationError("Invalid name, class access code or password")

        student = students[0]
        user = authenticate(username=student.new_user.username, password=password)

        if user is None:
            raise forms.ValidationError("Invalid name, class access code or password")
        if not user.is_active:
            raise forms.ValidationError("This user account has been deactivated")

        return student, user


class StudentEditAccountForm(forms.Form):
    name = forms.CharField(
        label='Name', max_length=100, required=False,
        widget=forms.TextInput(attrs={'placeholder': "Name"}))
    email = forms.EmailField(
        label='New email address (optional)', required=False,
        widget=forms.EmailInput(attrs={'placeholder': "new.address@myemail.com"}))
    password = forms.CharField(
        label='New password (optional)', required=False,
        widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm new password', required=False,
        widget=forms.PasswordInput)
    current_password = forms.CharField(
        label='Current password',
        widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(StudentEditAccountForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name', None)
        if not self.user.new_student.class_field:
            if name == '':
                raise forms.ValidationError("This field is required")

            if re.match(re.compile('^[\w ]+$'), name) is None:
                raise forms.ValidationError("Names may only contain letters, numbers, dashes, underscores, and spaces.")

        return name

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False, numbers=False):
            raise forms.ValidationError(
                "Password not strong enough, consider using at least 6 characters")

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        current_password = self.cleaned_data.get('current_password', None)

        if password is not None and (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError("Your new passwords do not match")

        if current_password and not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password was incorrect")

        return self.cleaned_data


class StudentSignupForm(forms.Form):
    name = forms.CharField(
        label='Name', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': "Rosalind Franklin"}))
    username = forms.CharField(
        label='Username', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': "rosie_f"}))
    email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'placeholder': "rosalind.franklin@cambridge.ac.uk"}))
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput)

    def clean_name(self):
        name = self.cleaned_data.get('name', None)
        if re.match(re.compile('^[\w ]+$'), name) is None:
            raise forms.ValidationError("Names may only contain letters, numbers, dashes, underscores, and spaces.")

        return name

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That username is already in use")

        if re.match(re.compile('[\w]+'), username) is None:
            raise forms.ValidationError("Usernames may only contain letters, numbers, dashes, and underscores.")

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False, numbers=False):
            raise forms.ValidationError("Password not strong enough, consider using at least 6 characters")

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Your passwords do not match")

        return self.cleaned_data


class IndependentStudentLoginForm(forms.Form):
    username = forms.CharField(
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': "rosie_f"}))
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput())

    captcha = ReCaptchaField()

    def clean(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)

        if username and password:
            students = Student.objects.filter(class_field=None, new_user__username=username)
            if not students.exists():
                raise forms.ValidationError("Incorrect username or password")

            user = authenticate(username=username, password=password)

            self.check_for_errors(user)

            self.user = user

        return self.cleaned_data

    def check_for_errors(self, user):
        if user is None:
            raise forms.ValidationError("Incorrect username or password")
        if not user.is_active:
            raise forms.ValidationError("This user account has been deactivated")


class StudentJoinOrganisationForm(forms.Form):
    access_code = forms.CharField(
        label='Class Access Code',
        widget=forms.TextInput(attrs={'placeholder': "AB123"}))

    def clean(self):
        access_code = self.cleaned_data.get('access_code', None)

        if access_code:
            classes = Class.objects.filter(access_code=access_code)
            if len(classes) != 1:
                raise forms.ValidationError("Cannot find the school or club and/or class")
            self.klass = classes[0]
            if not self.klass.always_accept_requests:
                if self.klass.accept_requests_until is None:
                    raise forms.ValidationError("Cannot find the school or club and/or class")
                elif (self.klass.accept_requests_until - timezone.now()) < timedelta():
                    raise forms.ValidationError("Cannot find the school or club and/or class")
        return self.cleaned_data
