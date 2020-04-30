from django.contrib.auth.views import LoginView
from django.core.urlresolvers import reverse_lazy

from portal.forms.play import StudentLoginForm


class StudentLoginView(LoginView):
    template_name = "portal/login/student.html"
    form_class = StudentLoginForm
    success_url = reverse_lazy("student_details")
    redirect_authenticated_user = reverse_lazy("student_details")

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url
