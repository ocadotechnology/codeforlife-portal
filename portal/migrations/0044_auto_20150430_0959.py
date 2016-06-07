# -*- coding: utf-8 -*-
# Code for Life
#
# Copyright (C) 2016, Ocado Innovation Limited
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
from __future__ import unicode_literals

from django.db import models, migrations
from portal.helpers import location

class Migration(migrations.Migration):

    # It will guess the country of the school using postcode, UK will be set if no result is returned by the API
    def populate_country(apps, schema_editor):

        School = apps.get_model("portal", "School")
        for school in School.objects.all():
            error, country, town, lat, lng = location.lookup_country(school.postcode)
            school.country = str(country)
            school.town = town
            school.lat = lat
            school.lng = lng
            school.save()

    def reset_country(apps, schema_editor):
        School = apps.get_model("portal", "School")
        for school in School.objects.all():
            school.country = ''
            school.town = '0'
            school.lat = '0'
            school.lng = '0'
            school.save()

    dependencies = [
        ('portal', '0043_auto_20150430_0952'),
    ]

    operations = [
        migrations.RunPython(populate_country, reset_country),
    ]
