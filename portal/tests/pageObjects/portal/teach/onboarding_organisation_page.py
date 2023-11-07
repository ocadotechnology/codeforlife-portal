from __future__ import absolute_import

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from . import onboarding_classes_page
from .teach_base_page import TeachBasePage


class OnboardingOrganisationPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingOrganisationPage, self).__init__(browser)

        assert self.on_correct_page("onboarding_organisation_page")

    def create_organisation(self, name, password, country="GB"):
        self._create_organisation(name, password, country)

        return onboarding_classes_page.OnboardingClassesPage(self.browser)

    def create_organisation_failure(self, name, password, country="GB"):
        self._create_organisation(name, password, country)

        return self

    def create_organisation_empty(self):
        self._click_create_school_button()

        return self

    def _create_organisation(self, name, password, country):
        self.browser.find_element(By.ID, "id_name").send_keys(name)
        country_element = self.browser.find_element(By.ID, "id_country")
        select = Select(country_element)
        select.select_by_value(country)
        self._click_create_school_button()

    def _click_create_school_button(self):
        self.browser.find_element(By.NAME, "create_organisation").click()

    def has_creation_failed(self):
        if not self.element_exists_by_css(".errorlist"):
            return False

        errors = (
            self.browser.find_element(By.ID, "form-create-organisation").find_element(By.CLASS_NAME, "errorlist").text
        )
        error = "There is already a school or club registered with that name and postcode"
        return error in errors

    def was_postcode_invalid(self):
        errors = (
            self.browser.find_element(By.ID, "form-create-organisation").find_element(By.CLASS_NAME, "errorlist").text
        )
        error = "Please enter a valid postcode or ZIP code"
        return error in errors
