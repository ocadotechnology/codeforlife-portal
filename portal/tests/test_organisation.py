from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher
from utils.organisation import create_organisation
from utils.messages import is_organisation_created_message_showing

class TestOrganisation(BaseTest):
    def test_create(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)

        page, name, postcode = create_organisation(page, password)
        assert is_organisation_created_message_showing(self.browser, name)

        page = page.goToOrganisationPage()
        assert page.is_admin_view()
        assert page.number_of_members() == 1
        assert page.number_of_admins() == 1

    def test_edit_details(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        page, name, postcode = create_organisation(page, password)

        page = page.goToOrganisationPage()
        assert page.checkOrganisationDetails({
            'name': name,
            'postcode': postcode
        })

        new_name = 'new ' + name
        new_postcode = 'OX2 6LE'

        page.changeOrganisationDetails({
            'name': new_name,
            'postcode': new_postcode
        })
        assert page.checkOrganisationDetails({
            'name': new_name,
            'postcode': new_postcode
        })

    def test_create_clash(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        page, name, postcode = create_organisation(page, password)

        page = page.logout().goToTeachPage()
        page, email, password = signup_teacher(page)
        page = page.login(email, password).goToOrganisationPage()
        page = page.create_organisation(name, postcode, password)
        
        assert page.has_creation_failed()

    def test_edit_clash(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        page, name, postcode = create_organisation(page, password)

        page = page.logout()
        page, email, password = signup_teacher(page)
        page = page.login(email, password)
        page, _, _ = create_organisation(page, password)
        page = page.goToOrganisationPage()

        assert not page.checkOrganisationDetails({
            'name': name,
            'postcode': postcode
        })

        page = page.changeOrganisationDetails({
            'name': name,
            'postcode': postcode
        })
        
        assert page.has_edit_failed()

    def test_revoke(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email_1, password_1 = signup_teacher(page)
        page = page.login(email_1, password_1)
        page, name, postcode = create_organisation(page, password_1)

        page = page.logout()
        page, email_2, password_2 = signup_teacher(page)
        page = page.login(email_2, password_2).goToOrganisationPage().join_organisation(name)
        assert page.__class__.__name__ == 'TeachOrganisationRevokePage'
        assert page.check_organisation_name(name, postcode)

        page = page.revoke_join()
        assert page.__class__.__name__ == 'TeachOrganisationCreatePage'

    def test_join(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page, email_1, password_1 = signup_teacher(page)
        page = page.login(email_1, password_1)
        page, name, postcode = create_organisation(page, password_1)

        page = page.logout()
        page, email_2, password_2 = signup_teacher(page)
        page = page.login(email_2, password_2).goToOrganisationPage().join_organisation(name)

        page = page.logout().goToTeachPage().login(email_1, password_1).goToOrganisationPage()
        assert page.have_join_request(email_2)
        page = page.accept_join_request(email_2)
        assert not page.have_join_request(email_2)
        assert page.number_of_members() == 2
        assert page.number_of_admins() == 1

        page = page.logout().goToTeachPage().login(email_2, password_2).goToOrganisationPage()
        assert page.check_organisation_name(name)
        assert not page.is_admin_view()

    def test_multiple_schools(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)

        # There was a bug where join requests to school 35 say would go to school 3,
        # 62 would go to 6, etc... this test checks for that

        n = 12

        emails = ['' for i in range(n)]
        passwords = ['' for i in range(n)]
        names = ['' for i in range(n)]
        postcodes = ['' for i in range(n)]

        for i in range(n):
            page, emails[i], passwords[i] = signup_teacher(page)
            page = page.login(emails[i], passwords[i])
            page, names[i], postcodes[i] = create_organisation(page, passwords[i])
            page = page.logout()

        page, email, password = signup_teacher(page)
        page = page.login(email, password).goToOrganisationPage().join_organisation(names[n-1])
        assert page.__class__.__name__ == 'TeachOrganisationRevokePage'
        assert page.check_organisation_name(names[n-1], postcodes[n-1])

        page = page.logout().goToTeachPage().login(emails[n-1], passwords[n-1]).goToOrganisationPage()
        assert page.have_join_request(email)
        page = page.accept_join_request(email)
        assert not page.have_join_request(email)
        assert page.number_of_members() == 2
        assert page.number_of_admins() == 1

        page = page.logout().goToTeachPage().login(email, password).goToOrganisationPage()
        assert page.check_organisation_name(names[n-1])
        assert not page.is_admin_view()
