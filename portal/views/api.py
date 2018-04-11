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
from django.http import HttpResponse

import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response

from django.contrib.auth.models import User
from portal.models import Teacher, Student


@api_view(('GET',))
def registered_users(request, year, month, day):
    try:
        nbr_reg = User.objects.filter(date_joined__startswith=datetime.date(int(year), int(month), int(day))).count()
        return Response(nbr_reg)
    except ValueError:
        return HttpResponse(status=404)


@api_view(('GET',))
def last_connected_since(request, year, month, day):
    try:
        nbr_active_users = User.objects.filter(last_login__gte=datetime.date(int(year), int(month), int(day))).count()
        return Response(nbr_active_users)
    except ValueError:
        return HttpResponse(status=404)


@api_view(('GET',))
def number_users_per_country(request, country):
    try:
        nbr_reg = Teacher.objects.filter(school__country__exact=country).count() + \
                  Student.objects.filter(class_field__teacher__school__country__exact=country).count()
        return Response(nbr_reg)
    except ValueError:
        return HttpResponse(status=404)
