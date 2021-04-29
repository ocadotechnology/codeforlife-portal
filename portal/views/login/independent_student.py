from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from portal.forms.play import IndependentStudentLoginForm
from portal.helpers.ratelimit import clear_ratelimit_cache


class IndependentStudentLoginView(LoginView):
    template_name = "portal/login/independent_student.html"
    form_class = IndependentStudentLoginForm
    success_url = reverse_lazy("student_details")
    redirect_authenticated_user = reverse_lazy("student_details")

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url

    def form_valid(self, form):
        # Reset ratelimit cache upon successful login
        clear_ratelimit_cache()

        return super(IndependentStudentLoginView, self).form_valid(form)
