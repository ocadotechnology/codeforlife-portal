from common.models import Student
from django.contrib.auth.views import LoginView
from django.shortcuts import render
from django.urls import reverse_lazy

from portal.forms.play import IndependentStudentLoginForm
from portal.helpers.ratelimit import clear_ratelimit_cache_for_user
from . import has_user_lockout_expired


class IndependentStudentLoginView(LoginView):
    template_name = "portal/login/independent_student.html"
    form_class = IndependentStudentLoginForm
    success_url = reverse_lazy("student_details")
    redirect_authenticated_user = reverse_lazy("student_details")

    def get_success_url(self):
        url = self.get_redirect_url()
        return url or self.success_url

    def post(self, request, *args, **kwargs):
        """
        If the email address inputted in the form corresponds to that of a blocked
        account, this redirects the user to the locked out page. However, if the lockout
        time is more than 24 hours before this is executed, the account is unlocked.
        """
        username = request.POST.get("username")
        if Student.objects.filter(new_user__username=username).exists():
            student = Student.objects.get(new_user__username=username)

            if student.blocked_time is not None:
                if has_user_lockout_expired(student):
                    student.blocked_time = None
                    student.save()
                else:
                    return render(
                        self.request,
                        "portal/locked_out.html",
                        {"is_teacher": False},
                    )

        return super(IndependentStudentLoginView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        # Reset ratelimit cache upon successful login
        clear_ratelimit_cache_for_user(form.cleaned_data["username"])
        return super().form_valid(form)
