from datetime import datetime, timedelta
import pytz

from django.urls import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm

# This import is required so that 2FA works properly
from portal import handlers

from portal.forms.teach import TeacherLoginForm
from portal.helpers.ratelimit import clear_ratelimit_cache
from portal.views.home import redirect_teacher_to_correct_page
from common.models import Teacher
from common.permissions import logged_in_as_teacher
from common.utils import using_two_factor


class TeacherLoginView(LoginView):
    template_name = "portal/login/teacher.html"
    form_class = TeacherLoginForm

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
        form = self.get_form()

        email = request.POST.get("username")
        teacher = Teacher.objects.get(new_user__email=email)

        if teacher.is_blocked:
            if datetime.now(tz=pytz.utc) - teacher.blocked_date < timedelta(hours=24):
                return render(
                    self.request,
                    "portal/locked_out.html",
                    {"is_teacher": True},
                )
            else:
                teacher.is_blocked = False
                teacher.save()

        if form.is_valid():
            # Reset ratelimit cache upon successful login
            clear_ratelimit_cache()

            user = form.get_user()
            if using_two_factor(user):
                return render(
                    self.request,
                    "portal/2FA_redirect.html",
                    {
                        "form": AuthenticationForm(),
                        "username": user.username,
                        "password": form.cleaned_data["password"],
                    },
                )
        return super(TeacherLoginView, self).post(request, *args, **kwargs)
