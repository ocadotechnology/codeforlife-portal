from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly
from utils.classes import create_class_directly
from utils.student import create_school_student_directly

class TestSchoolStudent(BaseTest):
    def test_login(self):
        email, password = signup_teacher_directly()
        org_name, postcode = create_organisation_directly(email)
        class_name, access_code = create_class_directly(email)
        student_name, student_password = create_school_student_directly(access_code)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).go_to_play_page().school_login(student_name, access_code, student_password)
        assert page.__class__.__name__ == 'PlayDashboardPage'
