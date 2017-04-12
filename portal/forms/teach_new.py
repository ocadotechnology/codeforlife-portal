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
import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from portal.models import Student, Teacher, stripStudentName
from portal.helpers.password import password_strength_test


choices = [('Miss', 'Miss'), ('Mrs', 'Mrs'), ('Ms', 'Ms'), ('Mr', 'Mr'),
           ('Dr', 'Dr'), ('Rev', 'Rev'), ('Sir', 'Sir'), ('Dame', 'Dame')]


class TeacherSignupForm(forms.Form):

    teacher_title = forms.ChoiceField(
        label='Title',
        choices=choices,
        widget=forms.Select(
            attrs={
                'class': 'wide'
            }
        )
    )
    teacher_first_name = forms.CharField(
        label='First name',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Grace'
            }
        )
    )
    teacher_last_name = forms.CharField(
        label='Last name',
        max_length=100,
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Hopper'
            }
        )
    )
    teacher_email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(
            attrs={
                'placeholder': 'grace.hopper@navy.mil'
            }
        )
    )
    teacher_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput()
    )
    teacher_confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput()
    )

    def clean_email(self):
        email = self.cleaned_data.get('teacher_email', None)

        if email and Teacher.objects.filter(new_user__email=email).exists():
            raise forms.ValidationError("That email address is already in use")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('teacher_password', None)

        if password and not password_strength_test(password):
            raise forms.ValidationError(
                "Password not strong enough, consider using at least 8 characters, upper and lower " + "case letters, and numbers")

        return password

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get('teacher_password', None)
        confirm_password = self.cleaned_data.get('teacher_confirm_password', None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Your passwords do not match')

        return self.cleaned_data


class TeacherEditAccountForm(forms.Form):

    title = forms.ChoiceField(
        label='Title', choices=choices,
        widget=forms.Select(attrs={'placeholder': "Title", 'class': 'wide'}))
    first_name = forms.CharField(
        label='First name', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': "First name", 'class': 'fName'}))
    last_name = forms.CharField(
        label='Last name', max_length=100,
        widget=forms.TextInput(attrs={'placeholder': "Last name", 'class': 'lName'}))
    email = forms.EmailField(
        label='Change email address (optional)', required=False,
        widget=forms.EmailInput(attrs={'placeholder': "new.email@address.com"}))
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
        super(TeacherEditAccountForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if email:
            teachers = Teacher.objects.filter(new_user__email=email)
            if (len(teachers) == 1 and teachers[0].new_user != self.user) or len(teachers) > 1:
                raise forms.ValidationError("That email address is already in use")

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password):
            raise forms.ValidationError(
                "Password not strong enough, consider using at least 8 characters, upper and lower " + "case letters, and numbers")

        return password

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        current_password = self.cleaned_data.get('current_password', None)

        self.check_password_errors(password, confirm_password, current_password)

        return self.cleaned_data

    def check_password_errors(self, password, confirm_password, current_password):
        if (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError('Your new passwords do not match')

        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your current password was incorrect')


class TeacherLoginForm(forms.Form):
    teacher_email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'placeholder': "my.email@address.com"}))
    teacher_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)

    def clean(self):
        if self.has_error('recaptcha'):
            raise forms.ValidationError('Incorrect email address, password or captcha')

        email = self.cleaned_data.get('teacher_email', None)
        password = self.cleaned_data.get('teacher_password', None)

        if email and password:

            # Check it's a teacher and not a student using the same email address
            user = None

            user = self.find_user(email, user)

            user = authenticate(username=user.username, password=password)

            self.check_email_erros(user)

            self.user = user

        return self.cleaned_data

    def find_user(self, email, user):
        users = User.objects.filter(email=email)

        for result in users:
            if hasattr(result, 'userprofile') and hasattr(result.userprofile, 'teacher'):
                user = result
                break

        if user is None:
            raise forms.ValidationError('Incorrect email address or password')

        return user

    def check_email_erros(self, user):
        if user is None:
            raise forms.ValidationError('Incorrect email address or password')

        if not user.is_active:
            raise forms.ValidationError('User account has been deactivated')


class ClassCreationForm(forms.Form):
    classmate_choices = [('True', 'Yes'), ('False', 'No')]
    class_name = forms.CharField(
        label='Class Name',
        widget=forms.TextInput(attrs={'placeholder': 'Lower KS2'}))
    classmate_progress = forms.ChoiceField(
        label="Allow students to see their classmates' progress?",
        choices=classmate_choices,
        widget=forms.Select(attrs={'class': 'wide'}))


def validateStudentNames(klass, names):
    validationErrors = []

    if klass:
        # We want to report if a student already exists with that name.
        # But only report each name once if there are duplicates.
        students = Student.objects.filter(class_field=klass)
        clashes_found = []
        find_clashes(names, students, clashes_found, validationErrors)

    # Also report if a student appears twice in the list to be added.
    # But again only report each name once.
    lower_names = [name.lower() for name in names]
    find_duplicates(names, lower_names, validationErrors)

    return validationErrors


def find_clashes(names, students, clashes_found, validationErrors):
    for name in names:
        if (students.filter(new_user__first_name__iexact=name).exists() and name not in clashes_found):
            validationErrors.append(forms.ValidationError("There is already a student called '" + name + "' in this class"))
            clashes_found.append(name)


def find_duplicates(names, lower_names, validationErrors):
    duplicates_found = []
    for duplicate in [name for name in names if lower_names.count(name.lower()) > 1]:
        if duplicate not in duplicates_found:
            validationErrors.append(forms.ValidationError(
                "You cannot add more than one student called '" + duplicate + "'"))
            duplicates_found.append(duplicate)


class StudentCreationForm(forms.Form):
    names = forms.CharField(label='names', widget=forms.Textarea)

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(StudentCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        names = re.split(';|,|\n', self.cleaned_data.get('names', ''))
        names = map(stripStudentName, names)
        names = [name for name in names if name != '']

        validationErrors = validateStudentNames(self.klass, names)

        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)

        self.strippedNames = names

        return self.cleaned_data
