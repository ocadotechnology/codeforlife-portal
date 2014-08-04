from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

from captcha.fields import ReCaptchaField

from postcodes import PostCoder

from models import Student, Class, School

from collections import Counter

class OrganisationCreationForm(forms.Form):
    name = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))
    current_password = forms.CharField(label='Confirm your password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm your password'}))
    postcode = forms.CharField(label="Postcode", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))
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
    fuzzy_name = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))

    # Note: the reason this is a CharField rather than a ChoiceField is to avoid having to provide choices
    # which was problematic given that the options are dynamically generated.
    chosen_org = forms.CharField(widget=forms.Select())

    def clean_chosen_org(self):
        chosen_org = self.cleaned_data.get('chosen_org', None)

        if chosen_org and not School.objects.filter(id=int(chosen_org)).exists():
            raise forms.ValidationError('That school/club was not recognised.')

        return chosen_org

class OrganisationEditForm(forms.Form):
    name = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))
    postcode = forms.CharField(label="Postcode", widget=forms.TextInput(attrs={'placeholder': 'Postcode'}))

    def __init__(self, *args, **kwargs):
        self.current_school = kwargs.pop('current_school', None)
        super(OrganisationEditForm, self).__init__(*args, **kwargs)

    def clean(self):
        name = self.cleaned_data.get('name', None)
        postcode = self.cleaned_data.get('postcode', None)

        if name and postcode:
            schools = School.objects.filter(name=name)
            if schools.exists() and schools[0].id != self.current_school.id:
                raise forms.ValidationError('There is already a school/club registered to that postcode.')

        return self.cleaned_data

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

class ClassMoveForm(forms.Form):
    new_teacher = forms.ChoiceField(label='Teachers')
    def __init__(self, teachers, *args, **kwargs):
        self.teachers = teachers
        teacher_choices = []
        for teacher in teachers:
            teacher_choices.append((teacher.id, teacher.name))
        super(ClassMoveForm, self).__init__(*args, **kwargs)
        self.fields['new_teacher'].choices = teacher_choices

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

class TeacherSetStudentPass(forms.Form):
    password = forms.CharField(label='New password', widget=forms.PasswordInput(attrs={'placeholder': 'New password'}))
    confirm_password = forms.CharField(label='Confirm new password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm new password'}))

    def clean(self):
        password = self.cleaned_data.get('password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)

        if (password or confirm_password) and password != confirm_password:
            raise forms.ValidationError('The new passwords do not match')

        return self.cleaned_data

class TeacherAddExternalStudentForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(TeacherAddExternalStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name=self.cleaned_data.get('name', None)
        students = Student.objects.filter(class_field=self.klass)
        if students.filter(name=name).exists():
            raise forms.ValidationError('A student already exists with that name in this class')
        return name

class TeacherMoveStudentsDestinationForm(forms.Form):
    new_class = forms.ChoiceField(label='Classes')
    def __init__(self, classes, *args, **kwargs):
        self.classes = classes
        class_choices = []
        for klass in classes:
            class_choices.append((klass.id, klass.name + ' (' + klass.access_code + '), ' + klass.teacher.name))
        super(TeacherMoveStudentsDestinationForm, self).__init__(*args, **kwargs)
        self.fields['new_class'].choices = class_choices

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
    first_name = forms.CharField(label='First name', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last name (optional)', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Last name (optional)'}))
    email = forms.EmailField(label='Email address (optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Email Address (optional)'}))
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

    def clean_email(self):
        email = self.cleaned_data.get('email', None)

        if email != '' and email != self.user.userprofile.user.email and User.objects.filter(email=email).exists():
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

class StudentSignupForm(forms.Form):
    first_name = forms.CharField(label='First name', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'First name'}))
    last_name = forms.CharField(label='Last name (optional)', required=False, max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Last name (optional)'}))
    username = forms.CharField(label='Username', max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    email = forms.EmailField(label='Email address (optional)', required=False, widget=forms.TextInput(attrs={'placeholder': 'Email Address (optional)'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirm_password = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))
    # captcha = ReCaptchaField()

    def clean_username(self):
        username = self.cleaned_data.get('username', None)
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('That username is already in use')

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', None)

        if email != '' and User.objects.filter(email=email).exists():
            raise forms.ValidationError('That email address is already in use')

        return email

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
    school = forms.CharField(label='School/club Name', widget=forms.TextInput(attrs={'placeholder': 'School/club Name'}))
    # captcha = ReCaptchaField()

    def clean(self):
        access_code = self.cleaned_data.get('access_code', None)
        school = self.cleaned_data.get('school', None)

        if access_code and school:
            classes = Class.objects.filter(access_code=access_code)
            if len(classes) != 1:
                raise forms.ValidationError('Cannot find the school/club and/or class.')
            klass = classes[0]
            if klass.teacher.school.name != school:
                raise forms.ValidationError('Cannot find the school/club and/or class.')
            self.klass = klass
        return self.cleaned_data

class ContactForm(forms.Form):
    name = forms.CharField(label='Name', widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email = forms.EmailField(label='Email address', widget=forms.TextInput(attrs={'placeholder': 'Email address'}))
    message = forms.CharField(label='Message', widget=forms.Textarea(attrs={'placeholder': 'Message'}))
