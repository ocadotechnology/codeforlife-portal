from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, FormView
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.utils.html import escape
from django.http import HttpResponseRedirect

from portal.forms.play import StudentLoginForm, StudentClassCodeForm
from common.models import UserSession, Student


class StudentClassCodeView(FormView):
    template_name = "portal/login/student_class_code.html"
    form_class = StudentClassCodeForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("student_details"))
        return super(StudentClassCodeView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        self.form = form
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        class_code = self.form.cleaned_data["access_code"]
        return reverse_lazy(
            "student_login",
            kwargs={"access_code": class_code},
        )


class StudentLoginView(LoginView):
    template_name = "portal/login/student.html"
    form_class = StudentLoginForm
    success_url = reverse_lazy("student_details")
    redirect_authenticated_user = reverse_lazy("student_details")

    def get_form_kwargs(self):
        kwargs = super(StudentLoginView, self).get_form_kwargs()
        kwargs["access_code"] = self.kwargs["access_code"]
        return kwargs

    def _add_logged_in_as_message(self, request):
        student = request.user.userprofile.student
        student_class = student.class_field
        student_school = student_class.teacher.school

        messages.info(
            request,
            (
                "You are logged in as a member of class: <strong>"
                + escape(student_class.name)
                + "</strong>, in school or club: <strong>"
                + escape(student_school.name)
                + "</strong>."
            ),
            extra_tags="safe",
        )

    def get_success_url(self):
        redirect_url = self.get_redirect_url()

        if redirect_url:
            return redirect_url

        self._add_logged_in_as_message(self.request)

        return self.success_url


def student_direct_login(request, user_id, login_id):
    """Direct login for student with unique url without username and password"""
    user = authenticate(request, user_id=user_id, login_id=login_id)

    if user:
        # Log the login time and class
        student = Student.objects.get(new_user=user)
        session = UserSession(user=user, class_field=student.class_field)
        session.save()

        login(request, user)
        return HttpResponseRedirect(reverse_lazy("student_details"))
    return HttpResponseRedirect(reverse_lazy("home"))
