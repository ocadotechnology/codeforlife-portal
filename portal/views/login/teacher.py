from common.models import Teacher
from common.permissions import logged_in_as_teacher
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from two_factor.views import LoginView
from two_factor.forms import AuthenticationTokenForm, BackupTokenForm

from portal.forms.teach import TeacherLoginForm
from portal.helpers.ratelimit import clear_ratelimit_cache
from portal.views.home import redirect_teacher_to_correct_page
from . import has_user_lockout_expired

# This import is required so that 2FA works properly
from portal import handlers


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

    def post(self, request, *args, **kwargs):
        """
        If the email address inputted in the form corresponds to that of a blocked
        account, this redirects the user to the locked out page. However, if the lockout
        time is more than 24 hours before this is executed, the account is unlocked.
        """
        form = self.get_form(data=self.request.POST)

        email = request.POST.get("auth-username")
        if Teacher.objects.filter(new_user__email=email).exists():
            teacher = Teacher.objects.get(new_user__email=email)

            if teacher.blocked_time is not None:
                if has_user_lockout_expired(teacher):
                    teacher.blocked_time = None
                    teacher.save()
                else:
                    return render(
                        self.request,
                        "portal/locked_out.html",
                        {"is_teacher": True},
                    )

        if form.is_valid():
            # Reset ratelimit cache upon successful login
            clear_ratelimit_cache()

        return super(TeacherLoginView, self).post(request, *args, **kwargs)
