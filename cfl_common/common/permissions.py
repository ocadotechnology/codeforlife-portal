from functools import wraps

from common.utils import using_two_factor
from django.http import Http404
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from rest_framework import permissions


def has_completed_auth_setup(u):
    return (not using_two_factor(u)) or (u.is_verified() and using_two_factor(u))


class LoggedInAsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return logged_in_as_teacher(request.user)


def logged_in_as_teacher(user):
    try:
        return user.userprofile.teacher and has_completed_auth_setup(user)
    except AttributeError:
        return False


def logged_in_as_student(u):
    try:
        if u.userprofile.student:
            return True
    except AttributeError:
        return False


def logged_in_as_independent_student(u):
    return logged_in_as_student(u) and u.userprofile.student.is_independent()


def logged_in_as_school_student(u):
    return logged_in_as_student(u) and not u.userprofile.student.is_independent()


def check_teacher_authorised(request, class_teacher):
    current_teacher_owns_the_class = class_teacher == request.user.new_teacher
    is_current_teacher_school_admin = (
        class_teacher.school == request.user.new_teacher.school and request.user.new_teacher.is_admin
    )

    if not (current_teacher_owns_the_class or is_current_teacher_school_admin):
        raise Http404


def not_logged_in(u):
    try:
        if u.userprofile:
            return False
    except AttributeError:
        return True


def not_fully_logged_in(u):
    return not_logged_in(u) or (not logged_in_as_student(u) and not logged_in_as_teacher(u))


def teacher_verified(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        u = request.user
        try:
            if not u.userprofile.teacher or not has_completed_auth_setup(u):
                return HttpResponseRedirect(reverse_lazy("teach"))
        except AttributeError:
            return HttpResponseRedirect(reverse_lazy("teach"))
        return view_func(request, *args, **kwargs)

    return wrapped


class CanDeleteGame(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        try:
            return u.userprofile.teacher and has_completed_auth_setup(u)
        except AttributeError:
            return False
