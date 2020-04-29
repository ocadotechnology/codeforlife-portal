from django.contrib.auth.views import LoginView
from django.core.urlresolvers import reverse_lazy

from portal.forms.play import StudentLoginForm


class StudentLoginView(LoginView):
    template_name = "portal/login/student.html"
    form_class = StudentLoginForm
    success_url = reverse_lazy("student_details")
    redirect_authenticated_user = reverse_lazy("student_details")
