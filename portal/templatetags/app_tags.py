# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2019, Ocado Innovation Limited
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
from aimmo.templatetags.players_utils import get_user_playable_games
from common.permissions import logged_in_as_teacher
from common.utils import using_two_factor
from django import template
from django.conf import settings
from django.shortcuts import reverse
from django.template.context import RequestContext
from django.template.defaultfilters import stringfilter
from portal import __version__, beta

register = template.Library()


@register.filter(name="emaildomain")
@stringfilter
def emaildomain(email):
    return "*********" + email[email.find("@") :]


@register.filter(name="has_2FA")
def has_2FA(u):
    return using_two_factor(u)


@register.filter(name="is_logged_in")
def is_logged_in(u):
    return (
        u
        and u.is_authenticated()
        and (not using_two_factor(u) or (hasattr(u, "is_verified") and u.is_verified()))
    )


@register.filter
def is_developer(u):
    return not u.is_anonymous() and u.userprofile.developer


@register.filter
def has_beta_access(request):
    return beta.has_beta_access(request)


@register.inclusion_tag("portal/partials/aimmo_games_table.html", takes_context=True)
def games_table(context, base_url):
    playable_games = get_user_playable_games(context, base_url)
    playable_games["can_delete_game"] = True

    user = context.request.user
    if (
        hasattr(user, "userprofile")
        and hasattr(user.userprofile, "student")
        and user.userprofile.student.class_field != None
    ):
        playable_games["can_delete_game"] = False

    return playable_games


@register.filter(name="make_into_username")
def make_into_username(u):
    username = ""
    if hasattr(u, "userprofile"):
        if hasattr(u.userprofile, "student"):
            username = u.first_name
        elif hasattr(u.userprofile, "teacher"):
            username = u.userprofile.teacher.title + " " + u.last_name

    return username


@register.filter(name="is_logged_in_as_teacher")
def is_logged_in_as_teacher(u):
    return is_logged_in(u) and u.userprofile and hasattr(u.userprofile, "teacher")


@register.filter(name="is_independent_student")
def is_independent_student(u):
    return (
        u.userprofile
        and u.userprofile.student
        and u.userprofile.student.is_independent()
    )


@register.filter(name="has_teacher_finished_onboarding")
def has_teacher_finished_onboarding(u):
    teacher = u.userprofile.teacher
    classes = teacher.class_teacher.all()
    return (
        is_logged_in_as_teacher(u)
        and teacher.has_school()
        and classes
        and (classes.count() > 1 or classes[0].has_students())
    )


@register.filter(name="is_logged_in_as_school_user")
def is_logged_in_as_school_user(u):
    return (
        is_logged_in(u)
        and u.userprofile
        and (
            (
                hasattr(u.userprofile, "student")
                and u.userprofile.student.class_field != None
            )
            or hasattr(u.userprofile, "teacher")
        )
    )


@register.filter(name="get_user_status")
def get_user_status(u):
    if is_logged_in_as_school_user(u):
        if is_logged_in_as_teacher(u):
            return "TEACHER"
        else:
            return "SCHOOL_STUDENT"
    elif is_logged_in(u):
        return "INDEPENDENT_STUDENT"
    else:
        return "UNTRACKED"


@register.filter(name="make_title_caps")
def make_title_caps(s):
    if len(s) > 0:
        s = s[0].upper() + s[1:]
    return s


@register.filter(name="cloud_storage")
@stringfilter
def cloud_storage(e):
    return settings.CLOUD_STORAGE_PREFIX + e


@register.filter(name="get_project_version")
def get_project_version():
    return __version__


@register.simple_tag(takes_context=True)
def url_for_aimmo_dashboard(context: RequestContext):
    if logged_in_as_teacher(context.request.user):
        return reverse("teacher_aimmo_dashboard")
    else:
        return reverse("student_aimmo_dashboard")
