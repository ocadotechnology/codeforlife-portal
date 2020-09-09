from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm

# This import is required so that 2FA works properly
from portal import handlers

from portal.forms.teach import TeacherLoginForm
from portal.views.home import redirect_teacher_to_correct_page
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

    def form_valid(self, form):
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
        return super(TeacherLoginView, self).form_valid(form)
