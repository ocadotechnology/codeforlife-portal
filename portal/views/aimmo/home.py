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
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.decorators import login_required

from portal.permissions import preview_user
from portal.views.teacher.teach import get_session_pdfs, get_resource_sheets_pdfs

from aimmo.app_settings import get_users_for_new_game
from aimmo.forms import AddGameForm


def save_form(request, create_game_form):
    game = create_game_form.save(commit=False)
    game.generator = "Main"
    game.owner = request.user
    game.main_user = request.user
    game.save()
    users = get_users_for_new_game(request)

    if users is not None:
        game.can_play.add(*users)
    return redirect("aimmo/play", id=game.id)


@login_required(login_url=reverse_lazy("login_view"))
@preview_user
def aimmo_home(request):
    aimmo_sessions = []
    aimmo_sheets = []

    get_session_pdfs("AIMMO_session_", aimmo_sessions)
    get_resource_sheets_pdfs(aimmo_sessions, "AIMMO_S", aimmo_sheets)

    playable_games = request.user.playable_games.all()

    if request.method == "POST":
        create_game_form = AddGameForm(playable_games, data=request.POST)
        if create_game_form.is_valid():
            return save_form(request, create_game_form)

    else:
        create_game_form = AddGameForm(playable_games)

    return render(
        request,
        "portal/aimmo_home.html",
        {
            "create_game_form": create_game_form,
            "aimmo_sessions": aimmo_sessions,
            "aimmo_sheets": aimmo_sheets,
        },
    )
