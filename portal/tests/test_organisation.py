from base_test import BaseTest
from portal.tests.pageObjects.portal.base_page import BasePage
from selenium.webdriver.support.ui import WebDriverWait

from portal.tests.pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation, create_organisation_directly
from utils.messages import is_organisation_created_message_showing

class TestOrganisation(BaseTest, BasePage):
    def test_create(self):
        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password)

        page, name, postcode = create_organisation(page, password)
        assert is_organisation_created_message_showing(self.browser, name)

        page = page.go_to_organisation_page()
        assert page.is_admin_view()
        assert page.number_of_members() == 1
        assert page.number_of_admins() == 1
        assert page.check_organisation_details({
            'name': name,
            'postcode': postcode
        })

    def test_edit_details(self):
        email, password = signup_teacher_directly()
        name, postcode = create_organisation_directly(email)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password).go_to_organisation_page()
        assert page.check_organisation_details({
            'name': name,
            'postcode': postcode
        })

        new_name = 'new ' + name
        new_postcode = 'OX2 6LE'

        page.change_organisation_details({
            'name': new_name,
            'postcode': new_postcode
        })
        assert page.check_organisation_details({
            'name': new_name,
            'postcode': new_postcode
        })

    def test_create_clash(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email_2, password_2).go_to_organisation_page()
        page = page.create_organisation(name, password_2, postcode)
        assert page.has_creation_failed()

    def test_edit_clash(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name_1, postcode_1 = create_organisation_directly(email_1)
        name_2, postcode_2 = create_organisation_directly(email_2)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email_2, password_2).go_to_organisation_page()

        assert not page.check_organisation_details({
            'name': name_1,
            'postcode': postcode_1
        })

        page = page.change_organisation_details({
            'name': name_1,
            'postcode': postcode_1
        })
        
        assert page.has_edit_failed()

    def test_revoke(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email_2, password_2).go_to_organisation_page()
        page = page.join_organisation(name)
        assert page.__class__.__name__ == 'TeachOrganisationRevokePage'
        assert page.check_organisation_name(name, postcode)

        page = page.revoke_join()
        assert page.__class__.__name__ == 'TeachOrganisationCreatePage'

    def test_join(self):
        email_1, password_1 = signup_teacher_directly()
        email_2, password_2 = signup_teacher_directly()
        name, postcode = create_organisation_directly(email_1)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email_2, password_2).go_to_organisation_page()
        page = page.join_organisation(name)

        page = page.logout().go_to_teach_page().login(email_1, password_1).go_to_organisation_page()
        assert page.have_join_request(email_2)
        page = page.accept_join_request(email_2)

        WebDriverWait(self.browser, 2).until_not(lambda driver: self.element_exists_by_id('request_table'))

        assert not page.have_join_request(email_2)
        assert page.number_of_members() == 2
        assert page.number_of_admins() == 1

        page = page.logout().go_to_teach_page().login(email_2, password_2).go_to_organisation_page()
        assert page.check_organisation_name(name)
        assert not page.is_admin_view()

    def test_multiple_schools(self):
        # There was a bug where join requests to school 35 say would go to school 3,
        # 62 would go to 6, etc... this test checks for that

        n = 12

        emails = ['' for i in range(n)]
        passwords = ['' for i in range(n)]
        names = ['' for i in range(n)]
        postcodes = ['' for i in range(n)]

        for i in range(n):
            emails[i], passwords[i] = signup_teacher_directly()
            names[i], postcodes[i] = create_organisation_directly(emails[i])

        email, password = signup_teacher_directly()

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_teach_page().login(email, password).go_to_organisation_page()
        page = page.join_organisation(names[n-1])
        assert page.__class__.__name__ == 'TeachOrganisationRevokePage'
        assert page.check_organisation_name(names[n-1], postcodes[n-1])

        page = page.logout().go_to_teach_page().login(emails[n-1], passwords[n-1]).go_to_organisation_page()
        assert page.have_join_request(email)
        page = page.accept_join_request(email)

        WebDriverWait(self.browser, 2).until_not(lambda driver: self.element_exists_by_id('request_table'))

        assert not page.have_join_request(email)
        assert page.number_of_members() == 2
        assert page.number_of_admins() == 1

        page = page.logout().go_to_teach_page().login(email, password).go_to_organisation_page()
        assert page.check_organisation_name(names[n-1])
        assert not page.is_admin_view()
