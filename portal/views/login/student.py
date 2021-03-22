from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.utils.html import escape

from portal.forms.play import StudentLoginForm


class StudentLoginView(LoginView):
    template_name = "portal/login/student.html"
    form_class = StudentLoginForm
    success_url = reverse_lazy("student_details")
    redirect_authenticated_user = reverse_lazy("student_details")

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
