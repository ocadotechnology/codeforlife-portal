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
from django.core.management import call_command
from django.test import TransactionTestCase

class MigrationTestCase(TransactionTestCase):
    """A Test case for testing migrations."""

    # These must be defined by subclasses.
    start_migration = None
    dest_migration = None
    django_application = None

    def setUp(self):
        super(MigrationTestCase, self).setUp()
        # Ensure the migration history is up-to-date with a fake migration.
        # The other option would be to use the south setting for these tests
        # so that the migrations are used to setup the test db.
        call_command('migrate', self.django_application, fake=True,
                     verbosity=0)
        # Then migrate back to the start migration.
        call_command('migrate', self.django_application, self.start_migration,
                     verbosity=0)

    def tearDown(self):
        # Leave the db in the final state so that the test runner doesn't
        # error when truncating the database.
        call_command('migrate', self.django_application, verbosity=0)

    def migrate_to_dest(self):
        call_command('migrate', self.django_application, self.dest_migration,
                     verbosity=0)

