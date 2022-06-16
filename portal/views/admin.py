from django.contrib import messages as messages
from django.contrib.auth import logout
from django.contrib.auth.views import (
    PasswordChangeView,
    PasswordChangeDoneView,
)
from django.http import HttpResponseRedirect
from rest_framework.reverse import reverse_lazy

from portal.forms.admin import AdminChangeOwnPasswordForm

block_limit = 5


class AdminChangePasswordView(PasswordChangeView):
    form_class = AdminChangeOwnPasswordForm
    success_url = reverse_lazy("administration_password_change_done")

    def form_valid(self, form):
        return super(AdminChangePasswordView, self).form_valid(form)


class AdminChangePasswordDoneView(PasswordChangeDoneView):
    def get(self, request, *args, **kwargs):
        logout(request)
        messages.success(
            request,
            "Password updated successfully. Please login using your new password.",
        )
        return HttpResponseRedirect(reverse_lazy("teacher_login"))
