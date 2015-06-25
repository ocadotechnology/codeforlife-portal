from base_test import BaseTest

from portal.tests.pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly
from utils.classes import create_class_directly
from utils.student import create_school_student_directly

class TestSchoolStudent(BaseTest):
    def test_login(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)\
            .go_to_play_page()\
            .school_login(student_name, access_code, student_password)
        assert self.is_dashboard(page)

    def test_login_failure(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)\
            .go_to_play_page()\
            .school_login(student_name, access_code, 'some other password')

        assert page.__class__.__name__ == 'PlayPage'
        assert page.school_login_has_failed()

    def test_change_password(self):
        email, password = signup_teacher_directly()
        create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.live_server_url)
        page = HomePage(self.browser).go_to_play_page()\
            .school_login(student_name, access_code, student_password)\
            .go_to_account_page()

        new_password = 'new ' + student_password
        page = page.change_details({
            'password': new_password,
            'confirm_password': new_password,
            'current_password': student_password
        })

        page = page.logout()\
            .go_to_play_page()\
            .school_login(student_name, access_code, student_password)

        assert page.school_login_has_failed()
        page = page.school_login(student_name, access_code, new_password)
        assert self.is_dashboard(page)

    def is_dashboard(self, page):
        return page.__class__.__name__ == 'PlayDashboardPage'
