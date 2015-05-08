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