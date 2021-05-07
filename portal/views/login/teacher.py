from django.urls import reverse_lazy
from django.shortcuts import redirect
from two_factor.views import LoginView
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm

# This import is required so that 2FA works properly
from portal import handlers

from portal.forms.teach import TeacherLoginForm
from portal.views.home import redirect_teacher_to_correct_page
from common.permissions import logged_in_as_teacher


class TeacherLoginView(LoginView):
    template_name = "portal/login/teacher.html"
    form_list = (
        ("auth", TeacherLoginForm),
        ("token", AuthenticationTokenForm),
        ("backup", BackupTokenForm),
    )

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if logged_in_as_teacher(request.user):
                return redirect(reverse_lazy("dashboard"))
            return redirect(reverse_lazy("home"))
        return super(TeacherLoginView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or redirect_teacher_to_correct_page(
            self.request, self.request.user.userprofile.teacher
        )
