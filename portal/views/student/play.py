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

from typing import Callable, Any, Dict, List

from aimmo.models import Game, Worksheet
from common import email_messages
from common.helpers.emails import send_email, NOTIFICATION_EMAIL
from common.permissions import logged_in_as_student, logged_in_as_independent_student
from django.contrib import messages as messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db.models import QuerySet
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView

from portal.forms.play import StudentJoinOrganisationForm
from portal.strings.student_aimmo_dashboard import AIMMO_DASHBOARD_BANNER


@login_required(login_url=reverse_lazy("student_login"))
@user_passes_test(logged_in_as_student, login_url=reverse_lazy("student_login"))
def student_details(request):
    return render(request, "portal/play/student_details.html")


def username_labeller(request):
    return request.user.username


@login_required(login_url=reverse_lazy("independent_student_login"))
@user_passes_test(
    logged_in_as_independent_student,
    login_url=reverse_lazy("independent_student_login"),
)
def student_join_organisation(request):

    student = request.user.new_student
    request_form = StudentJoinOrganisationForm()

    # check student not managed by a school
    if student.class_field:
        return HttpResponseRedirect(reverse_lazy("student_details"))

    if request.method == "POST":
        if "class_join_request" in request.POST:
            request_form = StudentJoinOrganisationForm(request.POST)
            process_join_organisation_form(request_form, request, student)

        elif "revoke_join_request" in request.POST:
            student.pending_class_request = None
            student.save()
            # Check teacher hasn't since accepted rejection before posting success
            show_cancellation_message_if_student_not_in_class(student, request)
            return HttpResponseRedirect(reverse_lazy("student_edit_account"))

    res = render(
        request,
        "portal/play/student_join_organisation.html",
        {"request_form": request_form, "student": student},
    )
    return res


def process_join_organisation_form(request_form, request, student):
    if request_form.is_valid():
        student.pending_class_request = request_form.klass
        student.save()

        email_message = email_messages.studentJoinRequestSentEmail(
            request,
            request_form.klass.teacher.school.name,
            request_form.klass.access_code,
        )
        send_email(
            NOTIFICATION_EMAIL,
            [student.new_user.email],
            email_message["subject"],
            email_message["message"],
        )

        email_message = email_messages.studentJoinRequestNotifyEmail(
            request,
            student.new_user.username,
            student.new_user.email,
            student.pending_class_request.access_code,
        )
        send_email(
            NOTIFICATION_EMAIL,
            [student.pending_class_request.teacher.new_user.email],
            email_message["subject"],
            email_message["message"],
        )

        messages.success(
            request, "Your request to join a school has been received successfully."
        )


def show_cancellation_message_if_student_not_in_class(student, request):
    if not student.class_field:
        messages.success(
            request, "Your request to join a school has been cancelled successfully."
        )


class StudentAimmoDashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "portal/play/student_aimmo_dashboard.html"

    login_url = reverse_lazy("student_login")

    def test_func(self) -> Callable:
        return logged_in_as_student

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        student = self.request.user.new_student
        klass = student.class_field

        try:
            aimmo_game = Game.objects.get(game_class=klass)

            active_worksheet = aimmo_game.worksheet
            inactive_worksheets = Worksheet.objects.exclude(id=active_worksheet.id)

            return {
                "BANNER": AIMMO_DASHBOARD_BANNER,
                "HERO_CARD": self._get_hero_card(active_worksheet, aimmo_game),
                "CARD_LIST": {"cards": self._get_card_list(inactive_worksheets)},
            }

        except ObjectDoesNotExist:
            return {"BANNER": AIMMO_DASHBOARD_BANNER}

    def _get_hero_card(
        self, active_worksheet: Worksheet, aimmo_game: Game
    ) -> Dict[str, Any]:
        return {
            "image": active_worksheet.active_image_path,
            "title": active_worksheet.name,
            "description": active_worksheet.description,
            "button1": {
                "text": "Read challenge",
                "url": "materials_viewer",
                "url_args": active_worksheet.student_pdf_name,
            },
            "button2": {
                "text": "Start challenge",
                "url": "kurono/play",
                "url_args": aimmo_game.id,
            },
        }

    def _get_card_list(self, inactive_worksheets: QuerySet) -> List[Dict[str, Any]]:
        card_list = []

        for inactive_worksheet in inactive_worksheets:
            worksheet_info = {
                "image": inactive_worksheet.image_path,
                "title": inactive_worksheet.name,
                "description": inactive_worksheet.short_description,
                "thumbnail_text": inactive_worksheet.thumbnail_text,
                "thumbnail_image": inactive_worksheet.thumbnail_image_path,
            }
            card_list.append(worksheet_info)

        kurono_feedback_card = {
            "image": "images/worksheets/kurono_logo.png",
            "title": "Let us know what you think",
            "button_text": "Give feedback",
            "button_link": "https://docs.google.com/forms/d/e/1FAIpQLSeI8Fu-tdtIseAaCrDbtOqtAK4x_-SWKttJYrbFx-j52fBYMA/viewform?usp=sf_link",
        }
        card_list.append(kurono_feedback_card)

        return card_list
