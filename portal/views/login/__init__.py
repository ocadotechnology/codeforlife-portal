from .teacher import TeacherLoginView
from .independent_student import IndependentStudentLoginView
from .student import StudentLoginView

from django.shortcuts import redirect
from django.urls import reverse_lazy


def old_login_form_redirect(request):
    return redirect(reverse_lazy("home"))
