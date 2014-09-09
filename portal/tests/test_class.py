from base_test import BaseTest

from pageObjects.portal.home_page import HomePage
from utils.teacher import signup_teacher_directly
from utils.organisation import create_organisation_directly
from utils.classes import create_class
from utils.messages import is_class_created_message_showing

class TestClass(BaseTest):
    def test_create(self):
        email, password = signup_teacher_directly()
        name, postcode = create_organisation_directly(email)

        self.browser.get(self.home_url)
        page = HomePage(self.browser).goToTeachPage().login(email, password).goToClassesPage()

        assert not page.have_classes()
        
        page, name, access_code = create_class(page)
        assert is_class_created_message_showing(self.browser, name)

        page = page.goToClassesPage()
        assert page.have_classes()
        assert page.does_class_exist(name, access_code)
