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
from typing import Any, Dict, List, Optional

from common.permissions import logged_in_as_student, logged_in_as_teacher
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse_lazy
from django.db.models import QuerySet
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView
from portal.strings.student_aimmo_dashboard import AIMMO_DASHBOARD_BANNER

from aimmo.forms import AddGameForm
from aimmo.game_creator import create_game
from aimmo.models import Game, Worksheet


class TeacherAimmoDashboard(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    login_url = reverse_lazy("teacher_login")
    form_class = AddGameForm
    template_name = "portal/aimmo_home.html"

    def test_func(self) -> Optional[bool]:
        return logged_in_as_teacher(self.request.user)

    def get_form(self, form_class=None):
        user = self.request.user
        classes = user.userprofile.teacher.class_teacher.all()
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(classes, **self.get_form_kwargs())

    def form_valid(self, form):
        create_game(self.request.user, form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("kurono/play", args=(self.object.id,))


class StudentAimmoDashboard(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "portal/play/student_aimmo_dashboard.html"

    login_url = reverse_lazy("student_login")

    def test_func(self) -> Optional[bool]:
        return logged_in_as_student(self.request.user)

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
