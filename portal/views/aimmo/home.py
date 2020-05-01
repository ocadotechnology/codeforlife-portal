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
from aimmo.app_settings import get_users_for_new_game
from aimmo.forms import AddGameForm
from aimmo.game_creator import create_game
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.edit import CreateView


class AimmoHomeView(LoginRequiredMixin, CreateView):
    login_url = reverse_lazy("student_login")
    form_class = AddGameForm
    template_name = "portal/aimmo_home.html"

    def get_form(self, form_class=None):
        user = self.request.user
        playable_games = user.playable_games.all()
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(playable_games, **self.get_form_kwargs())

    def form_valid(self, form):
        create_game(self.request.user, form, get_users_for_new_game(self.request))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("kurono/play", args=(self.object.id,))
