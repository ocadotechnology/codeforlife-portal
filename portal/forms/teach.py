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
import re

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from portal.models import Student, Teacher, stripStudentName
from portal.helpers.password import password_strength_test
from captcha.fields import ReCaptchaField


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

    def clean_teacher_password(self):
        password = self.cleaned_data.get('teacher_password', None)

        if password and not password_strength_test(password):
            raise forms.ValidationError(
                "Password not strong enough, consider using at least 8 characters, upper and lower case letters, and numbers")

        return password

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get('teacher_password', None)
        confirm_password = self.cleaned_data.get('teacher_confirm_password', None)

        check_passwords(password, confirm_password)

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
        check_passwords(password, confirm_password)

        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your current password was incorrect')


class TeacherLoginForm(forms.Form):
    teacher_email = forms.EmailField(
        label='Email address',
        widget=forms.EmailInput(attrs={'placeholder': "my.email@address.com"}))
    teacher_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput)

    captcha = ReCaptchaField()

    def clean(self):
        email = self.cleaned_data.get('teacher_email', None)
        password = self.cleaned_data.get('teacher_password', None)

        if email and password:

            # Check it's a teacher and not a student using the same email address
            user = None

            user = self.find_user(email, user)

            user = authenticate(username=user.username, password=password)

            self.check_email_errors(user)

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

    def check_email_errors(self, user):
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


class ClassEditForm(forms.Form):
    classmate_choices = [('True', 'Yes'), ('False', 'No')]
    # select dropdown choices for potentially limiting time in which external students may join
    # class
    # 0 value = don't allow
    # n value = allow for next n hours, n < 1000 hours
    # o/w = allow forever
    join_choices = [('', "Don't change my current setting"),
                    ('0', "Don't allow external requests to this class"),
                    ('1', "Allow external requests to this class for the next hour")]
    join_choices.extend([(str(hours), "Allow external requests to this class for the next " + str(hours) + " hours")
                         for hours in range(4, 24, 4)])
    join_choices.extend([(str(days*24), "Allow external requests to this class for the next " + str(days) + " days")
                         for days in range(2, 5)])
    join_choices.append(('1000', "Always allow external requests to this class (not recommended)"))
    name = forms.CharField(
        label='Class Name',
        widget=forms.TextInput(attrs={'placeholder': 'Class Name'}))
    classmate_progress = forms.ChoiceField(
        label="Allow students to see their classmates' progress?",
        choices=classmate_choices, widget=forms.Select(attrs={'class': 'wide'}))
    external_requests = forms.ChoiceField(
        label="Set up external requests to this class", required=False, choices=join_choices,
        widget=forms.Select(attrs={'class': 'wide'}))


class ClassMoveForm(forms.Form):
    new_teacher = forms.ChoiceField(label='Teachers', widget=forms.Select(attrs={'class': 'wide'}))

    def __init__(self, teachers, *args, **kwargs):
        self.teachers = teachers
        teacher_choices = []
        for teacher in teachers:
            teacher_choices.append((teacher.id, teacher.new_user.first_name + ' ' + teacher.new_user.last_name))
        super(ClassMoveForm, self).__init__(*args, **kwargs)
        self.fields['new_teacher'].choices = teacher_choices


class TeacherEditStudentForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))

    def __init__(self, student, *args, **kwargs):
        self.student = student
        self.klass = student.class_field
        super(TeacherEditStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get('name', ''))

        if name == '':
            raise forms.ValidationError("'" + self.cleaned_data.get('name', '') + "' is not a valid name")

        if re.match(re.compile('^[\w ]+$'), name) is None:
            raise forms.ValidationError("Names may only contain letters, numbers, dashes, underscores, and spaces.")

        students = Student.objects.filter(class_field=self.klass,
                                          new_user__first_name__iexact=name)
        if students.exists() and students[0] != self.student:
            raise forms.ValidationError("There is already a student called '" + name + "' in this class")

        return name


class TeacherSetStudentPass(forms.Form):
    password = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'placeholder': "New password"}))
    confirm_password = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput(attrs={'placeholder': "Confirm new password"}))

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False,
                                                   numbers=False):
            raise forms.ValidationError(
                "Password not strong enough, consider using at least 6 characters")

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        check_passwords(password, confirm_password)

        return self.cleaned_data


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

    find_illegal_characters(names, validationErrors)

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


def find_illegal_characters(names, validationErrors):
    for name in names:
        if re.match(re.compile('^[\w ]+$'), name) is None:
            validationErrors.append(forms.ValidationError(
                "Names may only contain letters, numbers, dashes, underscores, and spaces. You must rename '" + name + "'."))


def check_passwords(password, confirm_password):
    if password is not None and (password or confirm_password) and password != confirm_password:
        raise forms.ValidationError('The password and the confirmation password do not match')


class TeacherMoveStudentsDestinationForm(forms.Form):
    new_class = forms.ChoiceField(label='Choose a new class from the drop down menu for the selected students.', widget=forms.Select(attrs={'class': 'wide'}))

    def __init__(self, classes, *args, **kwargs):
        self.classes = classes
        class_choices = []
        for klass in classes:
            class_choices.append((klass.id, klass.name + ' (' + klass.access_code + '), ' + klass.teacher.new_user.first_name + ' ' + klass.teacher.new_user.last_name))
        super(TeacherMoveStudentsDestinationForm, self).__init__(*args, **kwargs)
        self.fields['new_class'].choices = class_choices


class TeacherMoveStudentDisambiguationForm(forms.Form):
    orig_name = forms.CharField(
        label='Original Name',
        widget=forms.TextInput(
            attrs={'readonly': 'readonly', 'placeholder': 'Original Name', 'type': 'hidden'}))
    name = forms.CharField(
        label='Name',
        widget=forms.TextInput(attrs={'placeholder': 'Name', 'style': 'margin : 0px'}))

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get('name', ''))
        if name == '':
            raise forms.ValidationError("'" + self.cleaned_data.get('name', '') + "' is not a valid name")
        return name


class BaseTeacherMoveStudentsDisambiguationFormSet(forms.BaseFormSet):
    def __init__(self, destination, *args, **kwargs):
        self.destination = destination
        super(BaseTeacherMoveStudentsDisambiguationFormSet, self).__init__(*args, **kwargs)

    def clean(self):
        if any(self.errors):
            return

        names = [form.cleaned_data['name'] for form in self.forms]

        validationErrors = validateStudentNames(self.destination, names)

        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)

        self.strippedNames = names


class TeacherDismissStudentsForm(forms.Form):
    orig_name = forms.CharField(
        label='Original Name',
        widget=forms.TextInput(
            attrs={'readonly': 'readonly', 'placeholder': 'Original Name', 'style': 'background-color: lightgray; margin: 0; border: 0'}))
    name = forms.CharField(
        label='New Name',
        widget=forms.TextInput(attrs={'placeholder': 'New Name', 'style': 'margin : 0px'}))
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address', 'style': 'margin : 0px'}))
    confirm_email = forms.EmailField(
        label='Confirm Email',
        widget=forms.EmailInput(
            attrs={'placeholder': 'Confirm Email Address', 'style': 'margin : 0px'}))

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get('name', ''))

        if name == '':
            raise forms.ValidationError("'" + self.cleaned_data.get('name', '') + "' is not a valid name")

        if User.objects.filter(username=name).exists():
            raise forms.ValidationError('That username is already in use')

        return name

    def clean(self):
        email = self.cleaned_data.get('email', None)
        confirm_email = self.cleaned_data.get('confirm_email', None)

        if (email or confirm_email) and email != confirm_email:
            raise forms.ValidationError('Your new emails do not match')

        return self.cleaned_data


class BaseTeacherDismissStudentsFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        names = [form.cleaned_data['name'] for form in self.forms]

        validationErrors = validateStudentNames(None, names)

        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)


class StudentCreationForm(forms.Form):
    names = forms.CharField(label='names', widget=forms.Textarea(
        attrs={
            'placeholder': 'You may type students names or copy and paste them from a spreadsheet into this text box.'
        }))

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


class TeacherAddExternalStudentForm(forms.Form):
    name = forms.CharField(
        label='Student name',
        widget=forms.TextInput(attrs={'placeholder': 'Name'}))

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(TeacherAddExternalStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get('name', ''))

        if name == '':
            raise forms.ValidationError("'" + self.cleaned_data.get('name', '') + "' is not a valid name")

        if Student.objects.filter(class_field=self.klass, new_user__first_name__iexact=name).exists():
            raise forms.ValidationError("There is already a student called '" + name + "' in this class")

        return name
