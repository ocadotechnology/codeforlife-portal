# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2020, Ocado Innovation Limited
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# ADDITIONAL TERMS – Section 7 GNU General Public Licence
#
# This licence does not grant any right, title or interest in any “Ocado” logos,
# trade names or the trademark “Ocado” or any other trademarks or domain names
# owned by Ocado Innovation Limited or the Ocado group of companies or any other
# distinctive brand features of “Ocado” as may be secured from time to time. You
# must not distribute any modification of this program using the trademark
# “Ocado” or claim any affiliation or association with Ocado or its employees.
#
# You are not authorised to use the name Ocado (or any of its trade names) or
# the names of any author or contributor in advertising or for publicity purposes
# pertaining to the distribution of this program, without the prior written
# authorisation of Ocado.
#
# Any propagation, distribution or conveyance of this program must include this
# copyright notice and these terms. You must not misrepresent the origins of this
# program; modified versions of the program must be marked as such and not
# identified as the original program.
from functools import wraps

from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from rest_framework import permissions

from common.utils import using_two_factor


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


def not_logged_in(u):
    try:
        if u.userprofile:
            return False
    except AttributeError:
        return True


def not_fully_logged_in(u):
    return not_logged_in(u) or (
        not logged_in_as_student(u) and not logged_in_as_teacher(u)
    )


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
