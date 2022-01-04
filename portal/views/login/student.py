from common.models import UserSession, Student, Class
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView, FormView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.html import escape

from portal.forms.play import StudentLoginForm, StudentClassCodeForm

import logging

LOGGER = logging.getLogger(__name__)


class StudentClassCodeView(FormView):
    template_name = "portal/login/student_class_code.html"
    form_class = StudentClassCodeForm

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        class_code = self.form.cleaned_data["access_code"].upper()
        return reverse_lazy(
            "student_login",
            kwargs={"access_code": class_code, "login_type": "classform"},
        )


class StudentLoginView(LoginView):
    """View for login with class link"""

    template_name = "portal/login/student.html"
    form_class = StudentLoginForm
    success_url = reverse_lazy("student_details")

    def get_form_kwargs(self):
        kwargs = super(StudentLoginView, self).get_form_kwargs()
        kwargs["access_code"] = self.kwargs["access_code"].upper()
        return kwargs

    def _add_logged_in_as_message(self, request):
        class_name = self.kwargs["access_code"].upper()
        messages.info(
            request,
            f"<strong>You are logged in to class: " f"{escape(class_name)}</strong>",
            extra_tags="safe message--student",
        )

    def get_success_url(self):
        redirect_url = self.get_redirect_url()

        if redirect_url:
            return redirect_url

        self._add_logged_in_as_message(self.request)

        return self.success_url

    def _add_login_data(self, form, login_type):
        # class and student have been validated by this point
        class_code = self.kwargs["access_code"]
        classes = Class.objects.filter(access_code__iexact=class_code)
        klass = classes[0]

        name = form.cleaned_data.get("username")
        students = Student.objects.filter(
            new_user__first_name__iexact=name, class_field=klass
        )
        try:
            student = students[0]
        except IndexError:
            msg = f"Student {name} in class {class_code} is not found!"
            LOGGER.error(msg)
            raise Exception(msg)

        # Log the login time, class, and login type
        session = UserSession(
            user=student.new_user, class_field=klass, login_type=login_type
        )
        session.save()

    def form_valid(self, form):
        """Security check complete. Log the user in."""

        login_type = self.kwargs["login_type"]
        if not login_type:
            login_type = "classlink"  # default if not specified

        self._add_login_data(form, login_type)
        return super(StudentLoginView, self).form_valid(form)


def student_direct_login(request, user_id, login_id):
    """Direct login for student with unique url without username and password"""
    user = authenticate(request, user_id=user_id, login_id=login_id)

    if user:
        # Log the login time and class
        student = Student.objects.get(new_user=user)
        session = UserSession(
            user=user, class_field=student.class_field, login_type="direct"
        )
        session.save()

        login(request, user)
        return HttpResponseRedirect(reverse_lazy("student_details"))
    return HttpResponseRedirect(reverse_lazy("home"))
