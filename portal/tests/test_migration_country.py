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
from base_test_migration import MigrationTestCase
from portal.tests.utils.organisation import create_organisation_directly
from portal.tests.utils.teacher import signup_teacher_directly
from portal.models import School
from mock import patch

# This test only tests migrations 0042 to 0045
class TestMigrationForCountry(MigrationTestCase):

    start_migration = '0042_school_country'
    dest_migration = '0045_auto_20150430_1446'

    django_application = 'portal'
    # Creating

    @patch('portal.helpers.location.lookup_country')
    def test_populating_valid_postcodes(self, mock_lookup_country):
        # Setting up mock
        values={(u'AL10 9NE'):(None, 'GB', 'Hatfield', 51.7623259, -0.2438929),
                (u'SW7 2AZ'):(None, 'GB', 'London', 51.5005046999999, -0.1782187),
                (u'CR3 7YA'):(None, 'GB', 'Caterham', 51.2763229, -0.051738),
                (u'10000'):(None, 'MX', 'Leon de los Aldama', 21.0859338, -101.5219684),
                (u'230-890'):(None, 'KR', 'Yeongwol-gun', 37.2382906, 128.5322833),
                (u'9446 PA'):(None, 'NL', 'Amen', 52.94067159999999, 6.6120059),
                }

        def side_effect(args):
            return values[args]

        mock_lookup_country.side_effect = side_effect

        # Creating Data
        email_address, password = signup_teacher_directly()

        organisations = []
        # Real postcodes from different countries
        organisations.append(create_organisation_directly(email_address, postcode = 'SW7 2AZ'))
        organisations.append(create_organisation_directly(email_address, postcode = 'CR3 7YA'))
        organisations.append(create_organisation_directly(email_address, postcode = '10000'))
        organisations.append(create_organisation_directly(email_address, postcode = '230-890'))
        organisations.append(create_organisation_directly(email_address, postcode = '9446 PA'))

        # Migrating
        self.migrate_to_dest()

        # Assertion: check that all the country fields are populated
        countries={(u'AL10 9NE'):('GB'),
                   (u'SW7 2AZ'):('GB'),
                   (u'CR3 7YA'):('GB'),
                   (u'10000'):('MX'),
                   (u'230-890'):('KR'),
                   (u'9446 PA'):('NL'),
                   }
        for organisation in organisations:
            school = School.objects.get(name=organisation[0])
            self.assertTrue(school.country, countries[school.postcode])

    @patch('portal.helpers.location.lookup_country')
    def test_populating_invalid_postcodes(self, mock_lookup_country):
        # Setting up mock
        values={(u'AL10 9NE'):(None, 'GB', 'Hatfield', 51.7623259, -0.2438929),
                (u'-----'):(None, 'GB', '0', 55.378051, -3.435973),
                (u'yyyyy'):(None, 'GB', '0', 55.378051, -3.435973),
                (u''):(None, 'GB', '0', 55.378051, -3.435973),
                }

        def side_effect(args):
            return values[args]

        mock_lookup_country.side_effect = side_effect

        # Creating Data
        email_address, password = signup_teacher_directly()

        organisations = []
        # invalid postcodes
        organisations.append(create_organisation_directly(email_address, postcode = '-----'))
        organisations.append(create_organisation_directly(email_address, postcode = 'yyyyy'))
        # as postcode should be required, this case in theory should not exist
        organisations.append(create_organisation_directly(email_address, postcode = ''))

        # Migrating
        self.migrate_to_dest()

        # Assertion: check that schools with invalid postcode will be set to default value, 'UK'
        countries={(u'AL10 9NE'):('GB'),
                (u'-----'):('GB'),
                (u'yyyyy'):('GB'),
                (u''):('GB'),
                }

        for organisation in organisations:
            school = School.objects.get(name=organisation[0])
            self.assertTrue(school.country, countries[school.postcode])