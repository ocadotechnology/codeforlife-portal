from common.helpers.emails import update_email
from common.models import Student
from common.permissions import logged_in_as_student
from django.contrib import messages as messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from portal.forms.play import StudentEditAccountForm, IndependentStudentEditAccountForm
from portal.helpers.password import check_update_password
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user


def _get_form(self, form_class):
    """
    Generic function which gets the appropriate edit account details form for either
    a school student or an independent student.
    :param self: The view class the form is used in.
    :param form_class: The form class which corresponds to the type of student.
    :return: The initialised form which can then be used in the FormView.
    """
    user = self.request.user
    if form_class is None:
        form_class = self.get_form_class()
    return form_class(user, **self.get_form_kwargs())


def _process_form(self, process_function, form, view):
    """
    Generic function which processes the appropriate edit account details form for
    either a school student or an independent student.
    :param self: The view class the form is used in.
    :param process_function: The core function that is needed to process the form.
    :param form: The form which needs to be processed.
    :param view: The view object.
    :return: The view once the form is valid and has been submitted.
    """
    student = self.request.user.new_student
    process_function(form, student, self.request)
    return super(view, self).form_valid(form)


class SchoolStudentEditAccountView(LoginRequiredMixin, FormView):
    """
    A FormView for editing a school student's account details. This forms enables a
    school student to change their password.
    """

    login_url = reverse_lazy("student_login")
    form_class = StudentEditAccountForm
    template_name = "../templates/portal/play/student_edit_account.html"
    success_url = reverse_lazy("student_details")
    model = Student

    def form_valid(self, form):
        return _process_form(
            self,
            self.process_student_edit_account_form,
            form,
            SchoolStudentEditAccountView,
        )

    def process_student_edit_account_form(self, form, student, request):
        data = form.cleaned_data
        # check not default value for CharField
        changing_password = check_update_password(form, student.new_user, request, data)

        messages.success(
            request, "Your account details have been changed successfully."
        )

        if changing_password:
            logout(request)
            messages.success(
                request,
                "Please login using your new password.",
            )
            return HttpResponseRedirect(reverse_lazy("student_login"))

    def get_form(self, form_class=None):
        return _get_form(self, form_class)


class IndependentStudentEditAccountView(LoginRequiredMixin, FormView):
    """
    A FormView for editing an independent student's account details. This forms enables
    an independent student to change their name, their email and / or their password.
    """

    login_url = reverse_lazy("independent_student_login")
    form_class = IndependentStudentEditAccountForm
    template_name = "../templates/portal/play/student_edit_account.html"
    model = Student
    initial = {"name": "Could not find name"}
    changing_email = False
    changing_password = False

    def get_form_kwargs(self):
        kwargs = super(IndependentStudentEditAccountView, self).get_form_kwargs()
        kwargs["initial"]["name"] = "{}{}".format(
            self.request.user.first_name, self.request.user.last_name
        )
        return kwargs

    def get_form(self, form_class=None):
        return _get_form(self, form_class)

    def get_success_url(self):
        if self.changing_email:
            return reverse_lazy("email_verification")
        elif self.changing_password:
            return reverse_lazy("independent_student_login")
        else:
            return reverse_lazy("student_details")

    def form_valid(self, form):
        return _process_form(
            self,
            self.process_independent_student_edit_account_form,
            form,
            IndependentStudentEditAccountView,
        )

    def process_independent_student_edit_account_form(self, form, student, request):
        data = form.cleaned_data

        # check not default value for CharField
        self.changing_password = check_update_password(
            form, student.new_user, request, data
        )

        # allow individual students to update more
        self.changing_email, new_email = update_email(student, request, data)

        self.update_name(student, data)

        # Reset ratelimit cache after successful account details update
        clear_ratelimit_cache_for_user(student.new_user.username)

        messages.success(
            request, "Your account details have been changed successfully."
        )

        if self.changing_email:
            logout(request)
            messages.success(
                request,
                "Your email will be changed once you have verified it, until then "
                "you can still log in with your old email.",
            )

        if self.changing_password:
            logout(request)
            messages.success(
                request,
                "Please login using your new password.",
            )

    def update_name(self, student, data):
        student.new_user.first_name = data["name"]
        # save all tables
        student.save()
        student.new_user.save()


@login_required(login_url=reverse_lazy("home"))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy("home"))
def student_edit_account(request):
    student = request.user.new_student
    if student.is_independent():
        return HttpResponseRedirect(reverse_lazy("independent_edit_account"))
    else:
        return HttpResponseRedirect(reverse_lazy("school_student_edit_account"))
