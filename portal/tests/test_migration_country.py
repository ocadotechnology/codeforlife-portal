from base_test_migration import MigrationTestCase
from portal.tests.utils.organisation import create_organisation_directly
from portal.tests.utils.teacher import signup_teacher_directly
from portal.models import School

# This test only tests migrations 0042 to 0045
class TestMigrationForCountry(MigrationTestCase):

    start_migration = '0042_school_country'
    dest_migration = '0045_auto_20150430_1446'
    django_application = 'portal'

    def test_populating_valid_postcodes(self):
        # Creating Data
        email_address, password = signup_teacher_directly()

        organisations = []
        organisations.append(create_organisation_directly(email_address, postcode = 'SW7 2AZ'))
        organisations.append(create_organisation_directly(email_address, postcode = 'CR3 7YA'))
        organisations.append(create_organisation_directly(email_address, postcode = '10000'))
        organisations.append(create_organisation_directly(email_address, postcode = '230-890'))
        organisations.append(create_organisation_directly(email_address, postcode = 'JMDCN06'))
        organisations.append(create_organisation_directly(email_address, postcode = '9446 PA'))

        # Migrating
        self.migrate_to_dest()

        # Assertion: check that all the country fields are populated
        for organisation in organisations:
            country = School.objects.get(name=organisation[0]).country
            self.assertTrue(country)

    def test_populating_invalid_postcodes(self):
        # Creating Data
        email_address, password = signup_teacher_directly()

        organisations = []
        organisations.append(create_organisation_directly(email_address, postcode = '-----'))
        organisations.append(create_organisation_directly(email_address, postcode = 'yyyyy'))
        # as postcode should be required, this case in theory should not exist
        organisations.append(create_organisation_directly(email_address, postcode = ''))

        # Migrating
        self.migrate_to_dest()

        # Assertion: check that schools with invalid postcode will be set to default value, 'UK'
        for organisation in organisations:
            country = School.objects.get(name=organisation[0]).country
            self.assertEqual('UK', country)
