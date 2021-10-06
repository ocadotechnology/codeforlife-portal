from __future__ import absolute_import

import time

from selenium.webdriver.support.ui import Select

from . import onboarding_classes_page
from . import onboarding_revoke_request_page
from .teach_base_page import TeachBasePage


class OnboardingOrganisationPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingOrganisationPage, self).__init__(browser)

        assert self.on_correct_page("onboarding_organisation_page")

    def create_organisation(self, name, password, postcode, country="GB"):
        self._create_organisation(name, password, postcode, country)

        return onboarding_classes_page.OnboardingClassesPage(self.browser)

    def create_organisation_failure(self, name, password, postcode, country="GB"):
        self._create_organisation(name, password, postcode, country)

        return self

    def create_organisation_empty(self):
        self._click_create_school_button()

        return self

    def join_empty_organisation(self):
        self.browser.find_element_by_id("join-tab").click()
        self._click_join_school_button()

        return self

    def _create_organisation(self, name, password, postcode, country):
        self.browser.find_element_by_id("id_name").send_keys(name)
        self.browser.find_element_by_id("id_postcode").send_keys(postcode)
        country_element = self.browser.find_element_by_id("id_country")
        select = Select(country_element)
        select.select_by_value(country)
        self._click_create_school_button()

    def _click_create_school_button(self):
        self.browser.find_element_by_name("create_organisation").click()

    def _click_join_school_button(self):
        self.browser.find_element_by_name("join_organisation").click()

    def has_creation_failed(self):
        if not self.element_exists_by_css(".errorlist"):
            return False

        errors = (
            self.browser.find_element_by_id("form-create-organisation")
            .find_element_by_class_name("errorlist")
            .text
        )
        error = (
            "There is already a school or club registered with that name and postcode"
        )
        return error in errors

    def was_postcode_invalid(self):
        errors = (
            self.browser.find_element_by_id("form-create-organisation")
            .find_element_by_class_name("errorlist")
            .text
        )
        error = "Please enter a valid postcode or ZIP code"
        return error in errors

    def join_organisation(self, name):
        self.browser.find_element_by_id("join-tab").click()
        self.browser.find_element_by_id("id_fuzzy_name").send_keys(name)
        time.sleep(1)
        self._click_join_school_button()

        if self.on_correct_page("onboarding_revoke_request_page"):
            return onboarding_revoke_request_page.OnboardingRevokeRequestPage(
                self.browser
            )
        else:
            return self
