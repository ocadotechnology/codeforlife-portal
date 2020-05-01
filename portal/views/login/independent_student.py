from django.contrib.auth.views import LoginView
from portal.forms.play import IndependentStudentLoginForm
from django.core.urlresolvers import reverse_lazy


class IndependentStudentLoginView(LoginView):
    template_name = "portal/login/independent_student.html"
    form_class = IndependentStudentLoginForm
    success_url = reverse_lazy("student_details")
    redirect_authenticated_user = reverse_lazy("student_details")

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url
