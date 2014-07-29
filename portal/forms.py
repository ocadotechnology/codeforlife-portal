from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from captcha.fields import ReCaptchaField

from models import Student, Class, School

from collections import Counter

class OrganisationCreationForm(forms.Form):
    school = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))
    current_password = forms.CharField(label='Confirm your password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))
    # captcha = ReCaptchaField()

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(OrganisationCreationForm, self).__init__(*args, **kwargs)

    def clean_school(self):
        school = self.cleaned_data.get('school', None)

        if school and School.objects.filter(name=school).exists():
            raise forms.ValidationError('That school/club name is already in use')

        return school

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password', None)
        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your password was incorrect')

class OrganisationJoinForm(forms.Form):
    school = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))
    
    def clean_school(self):
        school = self.cleaned_data.get('school', None)

        if school and not School.objects.filter(name=school).exists():
            raise forms.ValidationError('That school/club name was not recognised.')

        return school

class OrganisationEditForm(forms.Form):
    name = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))

    def __init__(self, *args, **kwargs):
        self.current_school = kwargs.pop('current_school', None)
        super(OrganisationEditForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name', None)

        if name:
            schools = School.objects.filter(name=name)
            if schools.exists() and schools[0].id != self.current_school.id:
                raise forms.ValidationError('That school/club name is already in use')

        return name

class TeacherSignupForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(label='Email address', widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))
    # captcha = ReCaptchaField()

    def clean_email(self):
        email = self.cleaned_data.get('email', None)

        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError('That email address is already in use')

        return email

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError('Your passwords do not match')

        return self.cleaned_data

class TeacherEditAccountForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name'}))
    email = forms.EmailField(label='Email address', widget=forms.TextInput(attrs={'placeholder': 'Email Address'}))
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
            users = User.objects.filter(email=email)
            if not (len(users) == 0 or (len(users) == 1 and users[0].email == self.user.email)):
                raise forms.ValidationError('That email address is already in use')

        return email

    def clean(self):
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
    # captcha = ReCaptchaField()

    def clean(self):
        email = self.cleaned_data.get('email', None)
        password = self.cleaned_data.get('password', None)

        if email and password:
            users = User.objects.filter(email=email)
            if len(users) != 1:
                raise forms.ValidationError('Incorrect email address or password')

            user = authenticate(username=users[0].username, password=password)

            if user is None:
                raise forms.ValidationError('Incorrect email address or password')
            if not user.is_active:
                raise forms.ValidationError('User account has been deactivated')

            self.user = user

        return self.cleaned_data

class ClassCreationForm(forms.Form):
    name = forms.CharField(label='Group Name', widget=forms.TextInput(attrs={'placeholder': 'Group Name'}))

class ClassEditForm(forms.Form):
    name = forms.CharField(label='Group Name', widget=forms.TextInput(attrs={'placeholder': 'Group Name'}))


class TeacherEditStudentForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    
    def __init__(self, student, *args, **kwargs):
        self.student = student
        self.klass = student.class_field
        super(TeacherEditStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name=self.cleaned_data.get('name', None)
        students = Student.objects.filter(class_field=self.klass)
        if students.filter(name=name).exists() and name != self.student.name:
            raise forms.ValidationError('A student already exists with that name in this class')
        return name


class StudentCreationForm(forms.Form):
    names = forms.CharField(label='names', widget=forms.Textarea)

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(StudentCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        names = self.cleaned_data.get('names', None).splitlines()
        names = [name for name in names if name != '']

        duplicates = [name for name, count in Counter(names).items() if count > 1]

        if len(duplicates) > 0:
            validationErrors = []
            for duplicate in duplicates:
                validationErrors.append(forms.ValidationError('Student ' + duplicate + ' cannot be added more than once'))
            raise forms.ValidationError(validationErrors)
        students = Student.objects.filter(class_field=self.klass)
        validationErrors = []
        for name in names:
             if students.filter(name=name).exists():
                 validationErrors.append(forms.ValidationError('A student already exists with the name ' + name))
        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)

        return self.cleaned_data


class StudentLoginForm(forms.Form):
    name =  forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    access_code = forms.CharField(label='Class Access Code', widget=forms.TextInput(attrs={'placeholder': 'Class Access Code'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    # captcha = ReCaptchaField()

    def clean(self):
        name = self.cleaned_data.get('name', None)
        access_code = self.cleaned_data.get('access_code', None)
        password = self.cleaned_data.get('password', None)

        if name and access_code and password:
            classes = Class.objects.filter(access_code=access_code)
            if len(classes) != 1:
                raise forms.ValidationError('Invalid name, class access code or password')

            students = Student.objects.filter(name=name, class_field=classes[0])
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
    password = forms.CharField(label='New password (optional)', required=False, widget=forms.PasswordInput(attrs={'placeholder': 'New password (optional)'}))
    confirm_password = forms.CharField(label='Confirm new password', required=False, widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))
    current_password = forms.CharField(label='Current password', widget=forms.PasswordInput(attrs={'placeholder': 'Current password'}))
    # captcha = ReCaptchaField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(StudentEditAccountForm, self).__init__(*args, **kwargs)

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        current_password = self.cleaned_data.get('current_password', None)

        if (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError('Your new passwords do not match')

        if not self.user.check_password(current_password):
            raise forms.ValidationError('Your current password was incorrect')

        return self.cleaned_data