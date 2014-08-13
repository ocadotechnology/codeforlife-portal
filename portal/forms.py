import re

from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.forms.formsets import BaseFormSet

from captcha.fields import ReCaptchaField

from postcodes import PostCoder

from models import Student, Class, School, Teacher, stripStudentName

from collections import Counter

def password_strength_test(password, length=8, upper=True, lower=True, numbers=True):
    return (len(password) >= length and
        (not upper or re.search(r'[A-Z]', password)) and
        (not lower or re.search(r'[a-z]', password)) and
        (not numbers or re.search(r'[0-9]', password)))

class OrganisationCreationForm(forms.Form):
    name = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))
    postcode = forms.CharField(label="Postcode", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))
    current_password = forms.CharField(label='Confirm your password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))
    # captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OrganisationCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        name = self.cleaned_data.get('name', None)
        postcode = self.cleaned_data.get('postcode', None)

        if name and postcode and School.objects.filter(name=name, postcode=postcode).exists():
            raise forms.ValidationError('There is already a school/club registered to that postcode.')

        return self.cleaned_data

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode', None)

        if postcode:
            result = PostCoder().get(postcode)
            if result:
                self.postcode_data = result
            else:
                raise forms.ValidationError('That postcode was not recognised.')

        return postcode

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password', None)
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your password was incorrect')

class OrganisationJoinForm(forms.Form):
    fuzzy_name = forms.CharField(label='Search for school or club by name or postcode', widget=forms.TextInput(attrs={'placeholder': 'Search for school or club by name or postcode'}))

    # Note: the reason this is a CharField rather than a ChoiceField is to avoid having to provide choices
    # which was problematic given that the options are dynamically generated.
    chosen_org = forms.CharField(label='Select school or club', widget=forms.Select(attrs={'class': 'wide'}))

    def clean_chosen_org(self):
        chosen_org = self.cleaned_data.get('chosen_org', None)

        if chosen_org and not School.objects.filter(id=int(chosen_org)).exists():
            raise forms.ValidationError('That school or club was not recognised.')

        return chosen_org

class OrganisationEditForm(forms.Form):
    name = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))
    postcode = forms.CharField(label="Postcode", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))

    def __init__(self, *args, **kwargs):
        self.current_school = kwargs.pop('current_school', None)
        super(OrganisationEditForm, self).__init__(*args, **kwargs)

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode', None)

        if postcode:
            result = PostCoder().get(postcode)
            if result:
                self.postcode_data = result
            else:
                raise forms.ValidationError('That postcode was not recognised.')
                
        return postcode

    def clean(self):
        name = self.cleaned_data.get('name', None)
        postcode = self.cleaned_data.get('postcode', None)

        if name and postcode:
            schools = School.objects.filter(name=name)
            if schools.exists() and schools[0].id != self.current_school.id:
                raise forms.ValidationError('There is already a school/club registered to that postcode.')

        return self.cleaned_data

class TeacherSignupForm(forms.Form):
    choices = [('Mr', 'Mr'), ('Master', 'Master'), ('Mrs', 'Mrs'), ('Miss', 'Miss'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Rev', 'Rev'), ('Sir', 'Sir'), ('Dame', 'Dame')]

    title = forms.ChoiceField(label='Title', choices=choices, widget=forms.Select(attrs={'placeholder': 'Title', 'class': 'wide'}))
    first_name = forms.CharField(label='First name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(label='Email address', widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))
    # captcha = ReCaptchaField()

    def clean_email(self):
        email = self.cleaned_data.get('email', None)

        if email and Teacher.objects.filter(user__user__email=email).exists():
            raise forms.ValidationError('That email address is already in use')

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password):
            raise forms.ValidationError('Password not strong enough, consider using at least 8 characters, upper and lower case letters, and numbers')

        return password

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Your passwords do not match')

        return self.cleaned_data

class TeacherEditAccountForm(forms.Form):
    choices = [('Mr', 'Mr'), ('Master', 'Master'), ('Mrs', 'Mrs'), ('Miss', 'Miss'), ('Ms', 'Ms'), ('Dr', 'Dr'), ('Rev', 'Rev'), ('Sir', 'Sir'), ('Dame', 'Dame')]

    title = forms.ChoiceField(label='Title', choices=choices, widget=forms.Select(attrs={'placeholder': 'Title', 'class': 'wide'}))
    first_name = forms.CharField(label='First name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name', 'class': 'fName'}))
    last_name = forms.CharField(label='Last name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name', 'class': 'lName'}))
    email = forms.EmailField(label='Change email address (optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Change email address (optional)'}))
    password = forms.CharField(label='New password (optional)', required=False, widget=forms.PasswordInput(attrs={'placeholder': 'New password (optional)'}))
    confirm_password = forms.CharField(label='Confirm new password', required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))
    current_password = forms.CharField(label='Current password', widget=forms.PasswordInput(attrs={'placeholder': 'Current password'}))
    # captcha = ReCaptchaField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TeacherEditAccountForm, self).__init__(*args, **kwargs)


    def clean_email(self):
        email = self.cleaned_data.get('email', None)
        if email:
            teachers = Teacher.objects.filter(user__user__email=email)
            if not (len(teachers) == 0 or (len(teachers) == 1 and users[0] == self.user)):
                raise forms.ValidationError('That email address is already in use')

        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password):
            raise forms.ValidationError('Password not strong enough, consider using at least 8 characters, upper and lower case letters, and numbers')

        return password

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        current_password = self.cleaned_data.get('current_password', None)

        if (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError('Your new passwords do not match')

        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your current password was incorrect')

        return self.cleaned_data


class TeacherLoginForm(forms.Form):
    email = forms.EmailField(label='Email address', widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        email = self.cleaned_data.get('email', None)
        password = self.cleaned_data.get('password', None)

        if email and password:
            users = User.objects.filter(email=email)

            # Check it's a teacher and not a student using the same email address
            user = None
            for result in users:
                if hasattr(result, 'userprofile') and hasattr(result.userprofile, 'teacher'):
                    user = result
                    break

            if user is None:
                raise forms.ValidationError('Incorrect email address or password')

            user = authenticate(username=user.username, password=password)

            if user is None:
                raise forms.ValidationError('Incorrect email address or password')
            if not user.is_active:
                raise forms.ValidationError('User account has been deactivated')

            self.user = user

        return self.cleaned_data

class ClassCreationForm(forms.Form):
    classmate_choices = [('True','Yes'), ('False','No')]
    name = forms.CharField(label='Group Name', widget=forms.TextInput(attrs={'placeholder': 'Group Name'}))
    classmate_progress = forms.ChoiceField(label="Allow students to see their classmates' progress?", choices=classmate_choices, widget=forms.Select(attrs={'class': 'wide'}))


class ClassEditForm(forms.Form):
    classmate_choices = [('True','Yes'), ('False','No')]
    # select dropdown choices for potentially limiting time in which external students may join class
    # 0 value = don't allow
    # n value = allow for next n hours, n < 1000 hours
    # o/w = allow forever
    join_choices = [('',"Don't change my current setting"),('0',"Don't allow external requests to this class"), ('1',"Allow external requests to this class for the next hour")]
    for i in range(5):
        hours = 4*(i+1)
        join_choices.append((str(hours), "Allow external requests to this class for the next " + str(hours) + " hours"))
    for i in range(5):
        days = i+1
        hours = days*24
        join_choices.append((str(days), "Allow external requests to this class for the next " + str(days) + " days"))
    join_choices.append(('1000', "Always allow external requests to this class (not recommended)"))
    name = forms.CharField(label='Group Name', widget=forms.TextInput(attrs={'placeholder': 'Group Name'}))
    classmate_progress = forms.ChoiceField(label="Allow students to see their classmates' progress?", choices=classmate_choices, widget=forms.Select(attrs={'class': 'wide'}))
    external_requests = forms.ChoiceField(label="Setup external requests to this class", required=False, choices=join_choices, widget=forms.Select(attrs={'class': 'wide'}))

class ClassMoveForm(forms.Form):
    new_teacher = forms.ChoiceField(label='Teachers')
    def __init__(self, teachers, *args, **kwargs):
        self.teachers = teachers
        teacher_choices = []
        for teacher in teachers:
            teacher_choices.append((teacher.id, teacher.user.user.first_name + ' ' + teacher.user.user.last_name))
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

        students = Student.objects.filter(class_field=self.klass, user__user__first_name__iexact=name)
        if students.exists() and students[0] != self.student:
             raise forms.ValidationError("There is already a student called '" + name + "' in this class")

        return name

class TeacherSetStudentPass(forms.Form):
    password = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={'placeholder': 'New password'}))
    confirm_password = forms.CharField(label='Confirm new password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False, numbers=False):
            raise forms.ValidationError('Password not strong enough, consider using at least 6 characters')

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password != None and (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError('The new passwords do not match')

        return self.cleaned_data

class TeacherAddExternalStudentForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(TeacherAddExternalStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get('name', ''))

        if name == '':
            raise forms.ValidationError("'" + self.cleaned_data.get('name', '') + "' is not a valid name")

        if Student.objects.filter(class_field=self.klass, user__user__first_name__iexact=name).exists():
             raise forms.ValidationError("There is already a student called '" + name + "' in this class")

        return name

class TeacherMoveStudentsDestinationForm(forms.Form):
    new_class = forms.ChoiceField(label='Classes')
    def __init__(self, classes, *args, **kwargs):
        self.classes = classes
        class_choices = []
        for klass in classes:
            class_choices.append((klass.id, klass.name + ' (' + klass.access_code + '), ' + klass.teacher.user.user.first_name + ' ' + klass.teacher.user.user.last_name))
        super(TeacherMoveStudentsDestinationForm, self).__init__(*args, **kwargs)
        self.fields['new_class'].choices = class_choices

class TeacherMoveStudentDisambiguationForm(forms.Form):
    orig_name = forms.CharField(label='Original Name', widget=forms.TextInput(attrs={'readonly':'readonly', 'placeholder': 'Original Name'}))
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get('name', ''))
        if name == '':
            raise forms.ValidationError("'" + self.cleaned_data.get('name', '') + "' is not a valid name")
        return name

def validateStudentNames(klass, names):
    validationErrors = []

    if klass:
        # We want to report if a student already exists with that name.
        # But only report each name once if there are duplicates.
        students = Student.objects.filter(class_field=klass)
        clashes_found = []
        for name in names:
            if students.filter(user__user__first_name__iexact=name).exists() and not name in clashes_found:
                 validationErrors.append(forms.ValidationError("There is already a student called '" + name + "' in this class"))
                 clashes_found.append(name)

    # Also report if a student appears twice in the list to be added.
    # But again only report each name once.
    lower_names = map(lambda x: x.lower(), names)
    duplicates = [name for name in names if lower_names.count(name.lower()) > 1]
    duplicates_found = []
    for duplicate in [name for name in names if lower_names.count(name.lower()) > 1]:
        if not duplicate in duplicates_found:
            validationErrors.append(forms.ValidationError("You cannot add more than one students called '" + duplicate + "'"))
            duplicates_found.append(duplicate)

    return validationErrors

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
    orig_name = forms.CharField(label='Original Name', widget=forms.TextInput(attrs={'readonly':'readonly', 'placeholder': 'Original Name'}))
    name = forms.CharField(label='New Name', widget=forms.TextInput(attrs={'placeholder': 'New Name'}))
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'placeholder': 'Email address'}))

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get('name', ''))

        if name == '':
            raise forms.ValidationError("'" + self.cleaned_data.get('name', '') + "' is not a valid name")

        if User.objects.filter(username=name).exists():
            raise forms.ValidationError('That username is already in use')

        return name


class BaseTeacherDismissStudentsFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        names = [form.cleaned_data['name'] for form in self.forms]

        validationErrors = validateStudentNames(None, names)

        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)

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

class StudentLoginForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    access_code = forms.CharField(label='Class Access Code', widget=forms.TextInput(attrs={'placeholder': 'Class Access Code'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    # captcha = ReCaptchaField()

    def clean(self):
        name = self.cleaned_data.get('name', None)
        access_code = self.cleaned_data.get('access_code', None)
        password = self.cleaned_data.get('password', None)

        if name and access_code and password:
            classes = Class.objects.filter(access_code__iexact=access_code)
            if len(classes) != 1:
                raise forms.ValidationError('Invalid name, class access code or password')

            name = stripStudentName(name)

            students = Student.objects.filter(user__user__first_name__iexact=name, class_field=classes[0])
            if len(students) != 1:
                raise forms.ValidationError('Invalid name, class access code or password')

            student = students[0]
            user = authenticate(username=student.user.user.username, password=password)

            if user is None:
                raise forms.ValidationError('Invalid name, class access code or password')
            if not user.is_active:
                raise forms.ValidationError('This user account has been deactivated')

            self.student = student
            self.user = user

        return self.cleaned_data

class StudentEditAccountForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email = forms.EmailField(label='Change email address (optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Change email address (optional)'}))
    password = forms.CharField(label='New password (optional)', required=False, widget=forms.PasswordInput(attrs={'placeholder': 'New password (optional)'}))
    confirm_password = forms.CharField(label='Confirm new password', required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))
    current_password = forms.CharField(label='Current password', widget=forms.PasswordInput(attrs={'placeholder': 'Current password'}))
    # captcha = ReCaptchaField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(StudentEditAccountForm, self).__init__(*args, **kwargs)

    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name', None)
        if not self.user.userprofile.student.class_field and first_name == '':
            raise forms.ValidationError('This field is required')
        return first_name

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False, numbers=False):
            raise forms.ValidationError('Password not strong enough, consider using at least 6 characters')

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        current_password = self.cleaned_data.get('current_password', None)

        if (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError('Your new passwords do not match')

        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your current password was incorrect')

        return self.cleaned_data

class StudentSignupForm(forms.Form):
    name = forms.CharField(label='Name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    username = forms.CharField(label='Username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(label='Email address', widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))
    # captcha = ReCaptchaField()

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('That username is already in use')

        return username

    def clean_password(self):
        password = self.cleaned_data.get('password', None)

        if password and not password_strength_test(password, length=6, upper=False, lower=False, numbers=False):
            raise forms.ValidationError('Password not strong enough, consider using at least 6 characters')

        return password

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Your passwords do not match')

        return self.cleaned_data

class StudentSoloLoginForm(forms.Form):
    username = forms.CharField(label='Username', widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    # captcha = ReCaptchaField()

    def clean(self):
        username = self.cleaned_data.get('username', None)
        password = self.cleaned_data.get('password', None)

        if username and password:
            students = Student.objects.filter(class_field=None, user__user__username=username)
            if not students.exists():
                raise forms.ValidationError('Incorrect username or password')

            user = authenticate(username=username, password=password)

            if user is None:
                raise forms.ValidationError('Incorrect username or password')
            if not user.is_active:
                raise forms.ValidationError('User account has been deactivated')

            self.user = user

        return self.cleaned_data


class StudentJoinOrganisationForm(forms.Form):
    access_code = forms.CharField(label='Class Access Code', widget=forms.TextInput(attrs={'placeholder': 'Class Access Code'}))
    # captcha = ReCaptchaField()

    def clean(self):
        access_code = self.cleaned_data.get('access_code', None)

        if access_code:
            classes = Class.objects.filter(access_code=access_code)
            if len(classes) != 1:
                raise forms.ValidationError('Cannot find the school/club and/or class.')
            self.klass = classes[0]
        return self.cleaned_data

class ContactForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email = forms.EmailField(label='Email address', widget=forms.TextInput(attrs={'placeholder': 'Email address'}))
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs={'placeholder': 'Message'}))
