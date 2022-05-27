from audioop import reverse
from traceback import print_list
from common.email_messages import accountDeletionEmail
from common.helpers.emails import NOTIFICATION_EMAIL, delete_contact, send_email, update_email
from common.models import Student
from common.permissions import logged_in_as_student
from django.contrib import messages as messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django import forms
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView, UpdateView
from django.shortcuts import render

from portal.forms.play import StudentEditAccountForm, IndependentStudentEditAccountForm
from portal.forms.registration import DeleteAccountForm

from portal.helpers.password import check_update_password
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user
from portal.views.api import anonymise


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

    login_url = reverse_lazy("student_login_access_code")
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

        messages.success(request, "Your account details have been changed successfully.")

        if changing_password:
            logout(request)
            messages.success(
                request,
                "Please login using your new password.",
            )
            return HttpResponseRedirect(reverse_lazy("student_login_access_code"))

    def get_form(self, form_class=None):
        return _get_form(self, form_class)


def independentStudentEditAccountView(request):
    """
    A FormView for editing an independent student's account details. This forms enables
    an independent student to change their name, their email and / or their password.
    Additionally it also deletes the independent students account with its second form

    Django class based views makes it very difficult to have multiple forms in one view,
    hence using the functional based view
    """
    user = request.user
    change_email_password_form = IndependentStudentEditAccountForm(user)
    delete_account_form = DeleteAccountForm(user)
    template_name = "../templates/portal/play/student_edit_account.html"
    delete_account_confirm = False

    def process_independent_student_edit_account_form(form, student, request):

        data = form
        if form.is_valid():
            data = form.cleaned_data

        # check not default value for CharField
        changing_password = check_update_password(form, student, request, data)

        # allow individual students to update more
        changing_email, new_email = update_email(student, request, data)

        update_name(student, data)

        # Reset ratelimit cache after successful account details update
        clear_ratelimit_cache_for_user(student.new_user.username)

        messages.success(request, "Your account details have been changed successfully.")

        if changing_email:
            logout(request)
            messages.success(
                request,
                "Your email will be changed once you have verified it, until then "
                "you can still log in with your old email.",
            )

        if changing_password:
            logout(request)
            messages.success(
                request,
                "Please login using your new password.",
            )

    def update_name(student, data):
        student.new_user.first_name = data["name"]
        # save all tables
        student.save()
        student.new_user.save()

    if request.method == "POST":
        if "delete_password" in request.POST:
            delete_account_form = DeleteAccountForm(user, request.POST)
            if not delete_account_form.is_valid():
                messages.warning(request, "Your account was not deleted due to incorrect password.")
                return render(
                    request,
                    template_name,
                    {"form": change_email_password_form, "delete_account_form": delete_account_form},
                )
            else:
                delete_account_confirm = True
                email = user.email
                anonymise(user)

                # remove from dotmailer
                if bool(request.POST.get("unsubscribe_newsletter")):
                    delete_contact(email)

                # send confirmation email
                message = accountDeletionEmail(request)
                send_email(
                    NOTIFICATION_EMAIL,
                    [email],
                    message["subject"],
                    message["message"],
                    message["title"],
                )

                return HttpResponseRedirect(reverse_lazy("home"))

        else:
            if not change_email_password_form.is_valid():
                messages.warning(request, "Your account was not updated do to incorrect details")
                return render(
                    request,
                    template_name,
                    {"form": change_email_password_form, "delete_account_form": delete_account_form},
                )
            else:
                process_independent_student_edit_account_form(change_email_password_form, user, request)

    return render(
        request,
        template_name,
        {
            "form": change_email_password_form,
            "delete_account_form": delete_account_form,
            "delete_account_confirm": delete_account_confirm,
        },
    )


class IndependentStudentEditAccountView(LoginRequiredMixin, FormView):

    login_url = reverse_lazy("independent_student_login")
    form_class = IndependentStudentEditAccountForm
    # second form for account deletion
    second_form_class = DeleteAccountForm
    template_name = "../templates/portal/play/student_edit_account.html"
    model = Student
    initial = {"name": "Could not find name"}
    changing_email = False
    changing_password = False

    # adding additional form into the forms simultaneously
    def get_context_data(self, **kwargs):
        context = super(IndependentStudentEditAccountView, self).get_context_data(**kwargs)
        if "form" not in context:
            context["form"] = self.form_class(request=self.request)
        if "delete_account_form" not in context:
            context["delete_account_form"] = self.second_form_class(user=self.request.user)
        return context

    def get_form(self, form_class=None):
        return _get_form(self, form_class)

    def post(self, request, *args, **kwargs):
        # making sure not both forms are submited

        if "delete_account" in request.POST:
            user = request.user
            password = request.POST.get("delete_password")
            form_class = self.second_form_class
            form_name = "delete_account_form"
            if not user.check_password(password):
                messages.warning(request, "Your account was not deleted due to incorrect password.")
            else:
                email = user.email
                anonymise(user)
                # remove the user from the newsletter subscription
                if bool(request.POST.get("unsubscribe_newsletter")):
                    delete_contact(email)
                message = accountDeletionEmail(request)
                send_email(NOTIFICATION_EMAIL, [email], message["subject"], message["message"], message["title"])
                return HttpResponseRedirect(reverse_lazy("home"))
        else:
            print("\n-----------" * 100)
            form_class = self.form_class
            form_name = "form"

        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(IndependentStudentEditAccountView, self).get_form_kwargs()
        kwargs["initial"]["name"] = "{}{}".format(self.request.user.first_name, self.request.user.last_name)
        return kwargs

    def get_success_url(self):
        if self.changing_email:
            return reverse_lazy("email_verification")
        elif self.changing_password:
            return reverse_lazy("independent_student_login")
        else:
            return reverse_lazy("independent_student_details")

    def form_valid(self, form):
        return _process_form(
            self,
            self.process_independent_student_edit_account_form,
            form,
            IndependentStudentEditAccountView,
        )


@login_required(login_url=reverse_lazy("home"))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy("home"))
def student_edit_account(request):
    student = request.user.new_student
    if student.is_independent():
        return HttpResponseRedirect(reverse_lazy("independent_edit_account"))
    else:
        return HttpResponseRedirect(reverse_lazy("school_student_edit_account"))
