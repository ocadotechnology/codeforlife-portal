import itertools
import re
from builtins import map, range, str

from common.helpers.emails import send_verification_email
from common.models import Student, Teacher, UserSession, stripStudentName
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible
from game.models import Episode, Worksheet

from portal.forms.error_messages import INVALID_LOGIN_MESSAGE
from portal.helpers.password import PasswordStrength, form_clean_password
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user


class InvitedTeacherForm(forms.Form):
    prefix = "teacher_signup"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["id"] = f"id_teacher_signup-{field_name}"

    teacher_password = forms.CharField(
        help_text="Enter a password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Password"}),
    )
    teacher_confirm_password = forms.CharField(
        help_text="Repeat password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Repeat password"}),
    )

    consent_ticked = forms.BooleanField(widget=forms.CheckboxInput(), initial=False, required=True)
    newsletter_ticked = forms.BooleanField(widget=forms.CheckboxInput(), initial=False, required=False)

    def clean_teacher_password(self):
        return form_clean_password(self, "teacher_password", PasswordStrength.TEACHER)

    def clean(self):
        if any(self.errors):
            return

        password = self.cleaned_data.get("teacher_password", None)
        confirm_password = self.cleaned_data.get("teacher_confirm_password", None)

        check_passwords(password, confirm_password)

        return self.cleaned_data


class TeacherSignupForm(InvitedTeacherForm):
    teacher_first_name = forms.CharField(
        help_text="Enter your first name",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "First name"}),
    )
    teacher_last_name = forms.CharField(
        help_text="Enter your last name",
        max_length=100,
        widget=forms.TextInput(attrs={"autocomplete": "off", "placeholder": "Last name"}),
    )
    teacher_email = forms.EmailField(
        help_text="Enter your email address",
        widget=forms.EmailInput(attrs={"autocomplete": "off", "placeholder": "Email address"}),
    )

    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible)


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
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password (optional)"}),
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
        widget=forms.EmailInput(attrs={"autocomplete": "off", "placeholder": "Email address"}),
        help_text="Enter your email address",
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Password"}),
        help_text="Enter your password",
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
            if hasattr(result, "userprofile") and hasattr(result.userprofile, "teacher"):
                user = result
                break

        if user is None:
            self.show_invalid_login_message()

        return user

    def check_email_errors(self, user):
        if user is None:
            self.show_invalid_login_message()

        if not user.userprofile.is_verified:
            send_verification_email(self.request, user, self.data)
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
    teacher = forms.ChoiceField(help_text="Select teacher", required=False)
    classmate_progress = forms.BooleanField(
        label="Allow students to see their classmates' progress?",
        widget=forms.CheckboxInput(),
        initial=False,
        required=False,
    )

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)

        if teacher is not None:
            # Place current teacher at the top
            teacher_choices = [
                (
                    teacher.id,
                    f"{teacher.new_user.first_name} {teacher.new_user.last_name}",
                )
            ]

            # Get coworkers and add them to the choices if the teacher is an admin
            if teacher.is_admin:
                coworkers = (
                    Teacher.objects.filter(school=teacher.school)
                    .exclude(id=teacher.id)
                    .order_by("new_user__last_name", "new_user__first_name")
                )
                for coworker in coworkers:
                    teacher_choices.append(
                        (
                            coworker.id,
                            f"{coworker.new_user.first_name} {coworker.new_user.last_name}",
                        )
                    )

            self.fields["teacher"].choices = teacher_choices

    def clean(self):
        name = self.cleaned_data.get("class_name", "")

        if re.match(re.compile("^[\w -]+$"), name) is None:
            raise forms.ValidationError(
                "Class name may only contain letters, numbers, dashes, underscores, and spaces."
            )

        return self.cleaned_data


class ClassEditForm(forms.Form):
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
                "Allow external requests to this class for the next " + str(hours) + " hours",
            )
            for hours in range(4, 28, 4)
        ]
    )
    join_choices.extend(
        [
            (
                str(days * 24),
                "Allow external requests to this class for the next " + str(days) + " days",
            )
            for days in range(2, 5)
        ]
    )
    join_choices.append(
        (
            "1000",
            "Always allow external requests to this class (not recommended)",
        )
    )
    name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Enter class name"}),
        help_text="Enter class name",
    )
    classmate_progress = forms.BooleanField(
        label="Allow students to see their classmates' progress?",
        widget=forms.CheckboxInput(),
        initial=False,
        required=False,
    )
    external_requests = forms.ChoiceField(
        label="Set up external requests to this class",
        help_text="Choose your setting",
        required=False,
        choices=join_choices,
        widget=forms.Select(),
    )

    def clean(self):
        name = self.cleaned_data.get("name", "")

        if re.match(re.compile("^[\w -]+$"), name) is None:
            raise forms.ValidationError(
                "Class name may only contain letters, numbers, dashes, underscores, and spaces."
            )

        return self.cleaned_data


class ClassLevelControlForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ClassLevelControlForm, self).__init__(*args, **kwargs)

        episodes = Episode.objects.filter(pk__in=range(1, 25))

        for episode in episodes:
            choices = []
            for level in episode.levels:
                try:
                    choices.append((f"worksheet:{level.after_worksheet.id}", episode.name))
                except Worksheet.DoesNotExist:
                    pass
                choices.append((f"level:{level.id}", level.name))

            for worksheet in episode.worksheets.filter(before_level__isnull=True):
                choices.append((f"worksheet:{worksheet.id}", episode.name))

            self.fields[f"episode{episode.id}"] = forms.MultipleChoiceField(
                choices=itertools.chain(choices),
                widget=forms.CheckboxSelectMultiple(),
                required=False,
            )


class ClassMoveForm(forms.Form):
    new_teacher = forms.ChoiceField(
        label="New teacher to take over class",
        help_text="Select teacher",
        widget=forms.Select(),
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
        label="Name",
        widget=forms.TextInput(attrs={"placeholder": "Name"}),
        help_text="Choose a name",
    )

    def __init__(self, student, *args, **kwargs):
        self.student = student
        self.klass = student.class_field
        super(TeacherEditStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get("name", ""))

        if name == "":
            raise forms.ValidationError("'" + self.cleaned_data.get("name", "") + "' is not a valid name")

        if re.match(re.compile("^[\w -]+$"), name) is None:
            raise forms.ValidationError("Names may only contain letters, numbers, dashes, underscores, and spaces.")

        students = Student.objects.filter(class_field=self.klass, new_user__first_name__iexact=name)
        if students.exists() and students[0] != self.student:
            raise forms.ValidationError("There is already a student called '" + name + "' in this class")

        return name


class TeacherSetStudentPass(forms.Form):
    password = forms.CharField(
        label="New password",
        help_text="Enter new password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Enter new password"}),
    )
    confirm_password = forms.CharField(
        label="Confirm new password",
        help_text="Confirm new password",
        widget=forms.PasswordInput(attrs={"autocomplete": "off", "placeholder": "Confirm new password"}),
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
        if students.filter(new_user__first_name__iexact=name).exists() and name not in clashes_found:
            validationErrors.append(
                forms.ValidationError("There is already a student called '" + name + "' in this class")
            )
            clashes_found.append(name)


def find_duplicates(names, lower_names, validationErrors):
    duplicates_found = []
    for duplicate in [name for name in names if lower_names.count(name.lower()) > 1]:
        if duplicate not in duplicates_found:
            validationErrors.append(
                forms.ValidationError("You cannot add more than one student called '" + duplicate + "'")
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
        raise forms.ValidationError("The password and the confirmation password do not match")


class TeacherMoveStudentsDestinationForm(forms.Form):
    new_class = forms.ChoiceField(
        label="Choose a new class from the drop down menu for the student(s).",
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
            raise forms.ValidationError("'" + self.cleaned_data.get("name", "") + "' is not a valid name")
        return name


class BaseTeacherMoveStudentsDisambiguationFormSet(forms.BaseFormSet):
    def __init__(self, destination, *args, **kwargs):
        self.destination = destination
        super(BaseTeacherMoveStudentsDisambiguationFormSet, self).__init__(*args, **kwargs)

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
        help_text="Original student name",
        widget=forms.TextInput(
            attrs={
                "readonly": "readonly",
                "placeholder": "Original Name",
                "class": "m-0",
            }
        ),
    )
    name = forms.CharField(
        help_text="New student name",
        widget=forms.TextInput(attrs={"placeholder": "Enter new student name", "class": "m-0"}),
    )
    email = forms.EmailField(
        label="Email",
        help_text="New email address",
        widget=forms.EmailInput(attrs={"placeholder": "Enter email address", "class": "m-0"}),
    )
    confirm_email = forms.EmailField(
        label="Confirm Email",
        help_text="Confirm email address",
        widget=forms.EmailInput(attrs={"placeholder": "Confirm email address", "class": "m-0"}),
    )

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get("name", ""))

        if name == "":
            raise forms.ValidationError("'" + self.cleaned_data.get("name", "") + "' is not a valid name")

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
                "placeholder": "You can import names from a .CSV file, or copy and paste them from a spreadsheet directly into this text box",
                "class": "m-0",
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
        label="Student name",
        widget=forms.TextInput(attrs={"placeholder": "Name"}),
    )

    def __init__(self, klass, *args, **kwargs):
        self.klass = klass
        super(TeacherAddExternalStudentForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = stripStudentName(self.cleaned_data.get("name", ""))

        if name == "":
            raise forms.ValidationError("'" + self.cleaned_data.get("name", "") + "' is not a valid name")

        if Student.objects.filter(class_field=self.klass, new_user__first_name__iexact=name).exists():
            raise forms.ValidationError("There is already a student called '" + name + "' in this class")

        return name
