from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm
from two_factor.views import LoginView

from portal.forms.teach import TeacherLoginForm


class TeacherLoginView(LoginView):
    TEMPLATES = {
        "auth": "portal/login/teacher.html",
        "token": "two_factor/core/login.html",
        "backup": "two_factor/core/login.html",
    }
    form_list = (
        ("auth", TeacherLoginForm),
        ("token", AuthenticationTokenForm),
        ("backup", BackupTokenForm),
    )
    template_name = "portal/login/teacher.html"
    success_url = reverse_lazy("dashboard")
    redirect_authenticated_user = reverse_lazy("dashboard")

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.redirect_authenticated_user)
        return super(TeacherLoginView, self).get(request, *args, **kwargs)
