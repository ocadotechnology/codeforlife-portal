import re
from builtins import map, range, str

from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Invisible
from common.helpers.emails import send_verification_email
from common.models import Student, stripStudentName, UserSession, Teacher
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from portal.helpers.password import PasswordStrength, form_clean_password
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user
from portal.templatetags.app_tags import is_verified


class TeacherSignupForm(forms.Form):

    teacher_first_name = forms.CharField(
        label="First name",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    teacher_last_name = forms.CharField(
        label="Last name",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off"}),
    )
    teacher_email = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(attrs={"autocomplete": "off"}),
    )

    newsletter_ticked = forms.BooleanField(
        widget=forms.CheckboxInput(), initial=False, required=False
    )

    teacher_password = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"autocomplete": "off"})
    )
    teacher_confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off"}),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)

    def clean_teacher_password(self):
        return form_clean_password(self, "teacher_password", PasswordStrength.TEACHER)

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get("teacher_password", None)
        confirm_password = self.cleaned_data.get("teacher_confirm_password", None)

        check_passwords(password, confirm_password)

        return self.cleaned_data


class TeacherEditAccountForm(forms.Form):

    first_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "First name", "class": "fName"}),
        help_text="First name",
    )
    last_name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Last name", "class": "lName"}),
        help_text="Last name",
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={"placeholder": "New email address (optional)"}),
        help_text="New email address (optional)",
    )
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"placeholder": "New password (optional)"}),
        help_text="New password (optional)",
    )
    confirm_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Confirm new password (optional)"}
        ),
        help_text="Confirm new password (optional)",
    )
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Current password"}),
        help_text="Enter your current password",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(TeacherEditAccountForm, self).__init__(*args, **kwargs)

    def clean_password(self):
        return form_clean_password(self, "password", PasswordStrength.TEACHER)

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get("password", None)
        confirm_password = self.cleaned_data.get("confirm_password", None)
        current_password = self.cleaned_data.get("current_password", None)

        self.check_password_errors(password, confirm_password, current_password)

        return self.cleaned_data

    def check_password_errors(self, password, confirm_password, current_password):
        check_passwords(password, confirm_password)

        if not self.user.check_password(current_password):
            raise forms.ValidationError("Your current password was incorrect")


class TeacherLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email address",
        widget=forms.EmailInput(
            attrs={"autocomplete": "off", "placeholder": "my.email@address.com"}
        ),
    )
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput(attrs={"autocomplete": "off"})
    )

    def clean(self):
        email = self.cleaned_data.get("username", None)
        password = self.cleaned_data.get("password", None)

        if email and password:

            # Check it's a teacher and not a student using the same email address
            user = None

            user = self.find_user(email, user)

            user = authenticate(username=user.username, password=password)

            self.check_email_errors(user)

            self.user_cache = user

            # Reset ratelimit cache upon successful login
            clear_ratelimit_cache_for_user(user.username)

            # Log the login time and school
            teacher = Teacher.objects.get(new_user=user)
            session = UserSession(user=user, school=teacher.school)
            session.save()

        return self.cleaned_data

    def find_user(self, email, user):
        users = User.objects.filter(email=email)

        for result in users:
            if hasattr(result, "userprofile") and hasattr(
                result.userprofile, "teacher"
            ):
                user = result
                break

        if user is None:
            self.show_invalid_login_message()

        return user

    def check_email_errors(self, user):
        if user is None:
            self.show_invalid_login_message()

        if not is_verified(user):
            send_verification_email(self.request, user)
            self.show_invalid_login_message()

        if not user.is_active:
            raise forms.ValidationError("User account has been deactivated")

    def show_invalid_login_message(self):
        raise forms.ValidationError(INVALID_LOGIN_MESSAGE)


class ClassCreationForm(forms.Form):
    class_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Class name"}),
        help_text="Enter a class name",
    )
    classmate_progress = forms.BooleanField(
        label="Allow students to see their classmates' progress",
        widget=forms.CheckboxInput(),
        initial=False,
        required=False,
    )


class ClassEditForm(forms.Form):
    classmate_choices = [("True", "Yes"), ("False", "No")]
    # select dropdown choices for potentially limiting time in which external students may join
    # class
    # 0 value = don't allow
    # n value = allow for next n hours, n < 1000 hours
    # o/w = allow forever
    join_choices = [
        ("", "Don't change my current setting"),
        ("0", "Don't allow external requests to this class"),
        ("1", "Allow external requests to this class for the next hour"),
    ]
    join_choices.extend(
        [
            (
                str(hours),
                "Allow external requests to this class for the next "
                + str(hours)
                + " hours",
            )
            for hours in range(4, 24, 4)
        ]
    )
    join_choices.extend(
        [
            (
                str(days * 24),
                "Allow external requests to this class for the next "
                + str(days)
                + " days",
            )
            for days in range(2, 5)
        ]
    )
    join_choices.append(
        ("1000", "Always allow external requests to this class (not recommended)")
    )
    name = forms.CharField(
        label="Class Name", widget=forms.TextInput(attrs={"placeholder": "Class Name"})
    )
    classmate_progress = forms.ChoiceField(
        label="Allow students to see their classmates' progress?",
        choices=classmate_choices,
        widget=forms.Select(attrs={"class": "wide"}),
    )
    external_requests = forms.ChoiceField(
        label="Set up external requests to this class",
        required=False,
        choices=join_choices,
        widget=forms.Select(attrs={"class": "wide"}),
    )


class ClassMoveForm(forms.Form):
    new_teacher = forms.ChoiceField(
        label="Teachers", widget=forms.Select(attrs={"class": "wide"})
    )

    def __init__(self, teachers, *args, **kwargs):
        self.teachers = teachers
        teacher_choices = []
        for teacher in teachers:
            teacher_choices.append(
                (
                    teacher.id,
                    teacher.new_user.first_name + " " + teacher.new_user.last_name,
                )
            )
        super(ClassMoveForm, self).__init__(*args, **kwargs)
        self.fields["new_teacher"].choices = teacher_choices


class TeacherEditStudentForm(forms.Form):
    name = forms.CharField(
        label="Name", widget=forms.TextInput(attrs={"placeholder": "Name"})
    )

    def __init__(self, student, *args, **kwargs):
        self.student = student
        self.klass = student.class_field
        super(TeacherEditStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get("name", ""))

        if name == "":
            raise forms.ValidationError(
                "'" + self.cleaned_data.get("name", "") + "' is not a valid name"
            )

        if re.match(re.compile("^[\w -]+$"), name) is None:
            raise forms.ValidationError(
                "Names may only contain letters, numbers, dashes, underscores, and spaces."
            )

        students = Student.objects.filter(
            class_field=self.klass, new_user__first_name__iexact=name
        )
        if students.exists() and students[0] != self.student:
            raise forms.ValidationError(
                "There is already a student called '" + name + "' in this class"
            )

        return name


class TeacherSetStudentPass(forms.Form):
    password = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={"placeholder": "New password"}),
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
    )

    def clean_password(self):
        return form_clean_password(self, "password", PasswordStrength.STUDENT)

    def clean(self):
        password = self.cleaned_data.get("password", None)
        confirm_password = self.cleaned_data.get("confirm_password", None)

        # Student password is case insensitive
        if password is not None:
            password = password.lower()

        if confirm_password is not None:
            confirm_password = confirm_password.lower()

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
        if (
            students.filter(new_user__first_name__iexact=name).exists()
            and name not in clashes_found
        ):
            validationErrors.append(
                forms.ValidationError(
                    "There is already a student called '" + name + "' in this class"
                )
            )
            clashes_found.append(name)


def find_duplicates(names, lower_names, validationErrors):
    duplicates_found = []
    for duplicate in [name for name in names if lower_names.count(name.lower()) > 1]:
        if duplicate not in duplicates_found:
            validationErrors.append(
                forms.ValidationError(
                    "You cannot add more than one student called '" + duplicate + "'"
                )
            )
            duplicates_found.append(duplicate)


def find_illegal_characters(names, validationErrors):
    for name in names:
        if re.match(re.compile("^[\w -]+$"), name) is None:
            validationErrors.append(
                forms.ValidationError(
                    "Names may only contain letters, numbers, dashes, underscores, and spaces. You must rename '"
                    + name
                    + "'."
                )
            )


def check_passwords(password, confirm_password):
    if password is not None and password != confirm_password:
        raise forms.ValidationError(
            "The password and the confirmation password do not match"
        )


class TeacherMoveStudentsDestinationForm(forms.Form):
    new_class = forms.ChoiceField(
        label="Choose a new class from the drop down menu for the selected students.",
        widget=forms.Select(attrs={"class": "wide"}),
    )

    def __init__(self, classes, *args, **kwargs):
        self.classes = classes
        class_choices = []
        for klass in classes:
            class_choices.append(
                (
                    klass.id,
                    klass.name
                    + " ("
                    + klass.access_code
                    + "), "
                    + klass.teacher.new_user.first_name
                    + " "
                    + klass.teacher.new_user.last_name,
                )
            )
        super(TeacherMoveStudentsDestinationForm, self).__init__(*args, **kwargs)
        self.fields["new_class"].choices = class_choices


class TeacherMoveStudentDisambiguationForm(forms.Form):
    orig_name = forms.CharField(
        label="Original Name",
        widget=forms.TextInput(
            attrs={
                "readonly": "readonly",
                "placeholder": "Original Name",
                "type": "hidden",
            }
        ),
    )
    name = forms.CharField(
        label="Name",
        widget=forms.TextInput(attrs={"placeholder": "Name", "style": "margin : 0px"}),
    )

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get("name", ""))
        if name == "":
            raise forms.ValidationError(
                "'" + self.cleaned_data.get("name", "") + "' is not a valid name"
            )
        return name


class BaseTeacherMoveStudentsDisambiguationFormSet(forms.BaseFormSet):
    def __init__(self, destination, *args, **kwargs):
        self.destination = destination
        super(BaseTeacherMoveStudentsDisambiguationFormSet, self).__init__(
            *args, **kwargs
        )

    def clean(self):
        if any(self.errors):
            return

        names = [form.cleaned_data["name"] for form in self.forms]

        validationErrors = validateStudentNames(self.destination, names)

        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)

        self.strippedNames = names


class TeacherDismissStudentsForm(forms.Form):
    orig_name = forms.CharField(
        label="Original Name",
        widget=forms.TextInput(
            attrs={
                "readonly": "readonly",
                "placeholder": "Original Name",
                "style": "background-color: lightgray; margin: 0; border: 0",
            }
        ),
    )
    name = forms.CharField(
        label="New Name",
        widget=forms.TextInput(
            attrs={"placeholder": "New Name", "style": "margin : 0px"}
        ),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "Email Address", "style": "margin : 0px"}
        ),
    )
    confirm_email = forms.EmailField(
        label="Confirm Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "Confirm Email Address", "style": "margin : 0px"}
        ),
    )

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get("name", ""))

        if name == "":
            raise forms.ValidationError(
                "'" + self.cleaned_data.get("name", "") + "' is not a valid name"
            )

        if User.objects.filter(username=name).exists():
            raise forms.ValidationError("That username is already in use")

        return name

    def clean(self):
        email = self.cleaned_data.get("email", None)
        confirm_email = self.cleaned_data.get("confirm_email", None)

        if (email or confirm_email) and email != confirm_email:
            raise forms.ValidationError("Your new emails do not match")

        return self.cleaned_data


class BaseTeacherDismissStudentsFormSet(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return

        names = [form.cleaned_data["name"] for form in self.forms]

        validationErrors = validateStudentNames(None, names)

        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)


class StudentCreationForm(forms.Form):
    names = forms.CharField(
        label="names",
        widget=forms.Textarea(
            attrs={
                "placeholder": "You may type students names or copy and paste them from a spreadsheet into this text box."
            }
        ),
    )

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(StudentCreationForm, self).__init__(*args, **kwargs)

    def clean(self):
        names = re.split(";|,|\n", self.cleaned_data.get("names", ""))
        names = list(map(stripStudentName, names))
        names = [name for name in names if name != ""]

        validationErrors = validateStudentNames(self.klass, names)

        if len(validationErrors) > 0:
            raise forms.ValidationError(validationErrors)

        self.strippedNames = names

        return self.cleaned_data


class TeacherAddExternalStudentForm(forms.Form):
    name = forms.CharField(
        label="Student name", widget=forms.TextInput(attrs={"placeholder": "Name"})
    )

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(TeacherAddExternalStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get("name", ""))

        if name == "":
            raise forms.ValidationError(
                "'" + self.cleaned_data.get("name", "") + "' is not a valid name"
            )

        if Student.objects.filter(
            class_field=self.klass, new_user__first_name__iexact=name
        ).exists():
            raise forms.ValidationError(
                "There is already a student called '" + name + "' in this class"
            )

        return name
