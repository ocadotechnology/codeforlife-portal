from django.contrib.auth.views import LoginView
from portal.forms.teach import TeacherLoginForm
from django.core.urlresolvers import reverse_lazy


class TeacherLoginView(LoginView):
    authentication_form = TeacherLoginForm
    template_name = "portal/login/teacher.html"
    success_url = "portal/email_verification_needed.html"
    redirect_authenticated_user = reverse_lazy("dashboard")
