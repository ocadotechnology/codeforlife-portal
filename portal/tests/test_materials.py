# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2017, Ocado Limited
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
from django.test import TestCase
from portal.templatetags.table_tags import resource_sheets_table, lengthen_list


class MaterialsTests(TestCase):
    def test_lengthen_list_when_length_is_bigger(self):
        li = [1, 2, 3, 4]
        length = 10
        result = lengthen_list(length, li)
        assert len(result) == 10

    def test_lengthen_list_when_length_is_same(self):
        li = [1, 2, 3, 4]
        length = 4
        result = lengthen_list(length, li)
        assert len(result) == 4

    def test_lengthen_list_when_length_is_smaller(self):
        li = [1, 2, 3, 4]
        length = 2
        result = lengthen_list(length, li)
        assert len(result) == 4

    def test_padding_resource_sheet_table(self):
        table = [[1, 2], [1, 2, 3], []]
        result = resource_sheets_table(table)
        assert result['table'] == [[1, 2, []], [1, 2, 3], [[], [], []]]
