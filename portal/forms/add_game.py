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
from common.models import Class
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.forms import ModelChoiceField, ModelForm, Select

from aimmo.models import Game, Worksheet


class AddGameForm(ModelForm):
    def __init__(self, classes: QuerySet, *args, **kwargs):
        super(AddGameForm, self).__init__(*args, **kwargs)
        self.fields["game_class"].queryset = classes

    game_class = ModelChoiceField(
        queryset=None, widget=Select, label="Class", required=True
    )

    class Meta:
        model = Game
        fields = [
            "game_class",
        ]

    def full_clean(self) -> None:
        super(AddGameForm, self).full_clean()
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            self._update_errors(e)

    def clean(self):
        game_class: Class = self.cleaned_data.get("game_class")

        if game_class and not Class.objects.filter(pk=game_class.id).exists():
            raise ValidationError("Sorry, an invalid class was entered")

        return self.cleaned_data
