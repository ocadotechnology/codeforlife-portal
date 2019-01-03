# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2018, Ocado Innovation Limited
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
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from aimmo.models import Game


class AddGameForm(ModelForm):
    class Meta:
        model = Game
        name = ['name']
        exclude = ['Main', 'owner', 'auth_token', 'completed', 'main_user', 'static_data', 'can_play',
                   'public', 'generator', 'target_num_cells_per_avatar',
                   'target_num_score_locations_per_avatar', 'score_despawn_chance',
                   'target_num_pickups_per_avatar', 'pickup_spawn_chance', 'obstacle_ratio',
                   'start_height', 'start_width']

    def clean(self):
        name = self.cleaned_data['name']

        playable_games_names = [
            playable_game.name
            for playable_game in self.playable_games
            if self.playable_games and name
        ]

        if name in playable_games_names:
            raise ValidationError("Sorry, a game with that name already exists.")

        return self.cleaned_data

    def add_playable_games(self, playable_games):
        self.playable_games = playable_games
