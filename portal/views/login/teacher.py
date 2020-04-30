from django.contrib.auth import login
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.utils.http import is_safe_url
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm
from two_factor.views import LoginView

from portal.forms.teach import TeacherLoginForm
from portal.views.home import redirect_teacher_to_correct_page


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
    redirect_authenticated_user = reverse_lazy("dashboard")

    def get_template_names(self):
        return [self.TEMPLATES[self.steps.current]]

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect(self.redirect_authenticated_user)
        return super(TeacherLoginView, self).get(request, *args, **kwargs)

    def done(self, form_list, **kwargs):
        user = self.get_user()
        login(self.request, user)

        redirect_to = self.request.POST.get(
            self.redirect_field_name, self.request.GET.get(self.redirect_field_name, "")
        )

        if not is_safe_url(url=redirect_to, allowed_hosts=[self.request.get_host()]):
            redirect_to = redirect_teacher_to_correct_page(
                self.request, user.userprofile.teacher
            )

        device = getattr(self.get_user(), "otp_device", None)
        if device:
            signals.user_verified.send(
                sender=__name__,
                request=self.request,
                user=self.get_user(),
                device=device,
            )
        return redirect(redirect_to)
