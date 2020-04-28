from django.contrib.auth.views import LoginView
from portal.forms.teach import TeacherLoginForm


class TeacherLoginView(LoginView):
    authentication_form = TeacherLoginForm
    template_name = "portal/login/teacher.html"
    success_url = "portal/email_verification_needed.html"

