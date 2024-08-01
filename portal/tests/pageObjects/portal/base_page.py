from __future__ import absolute_import

import time
from builtins import object

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

FADE_TIME = 0.5


class BasePage(object):
    browser = None

    DEFAULT_WAIT_SECONDS = 5

    def __init__(self, browser):
        self.browser = browser

    def wait_for_element_by_id(self, id, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_for_presence((By.ID, id), wait_seconds)

    def wait_for_element_by_css(self, css, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_for_presence((By.CSS_SELECTOR, css), wait_seconds)

    def wait_for_element_to_be_clickable(
        self, locator, wait_seconds=DEFAULT_WAIT_SECONDS
    ):
        self.wait(EC.element_to_be_clickable(locator), wait_seconds)

    def wait_for_element_to_be_invisible(
        self, locator, wait_seconds=DEFAULT_WAIT_SECONDS
    ):
        self.wait(EC.invisibility_of_element_located(locator), wait_seconds)

    def wait_for_presence(self, locator, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait(EC.presence_of_element_located(locator), wait_seconds)

    def wait_for_absence(self, locator, wait_seconds=DEFAULT_WAIT_SECONDS):
        self.wait_until_not(
            EC.presence_of_element_located(locator), wait_seconds
        )

    def wait(self, method, wait_seconds=DEFAULT_WAIT_SECONDS):
        WebDriverWait(self.browser, wait_seconds).until(method)

    def wait_until_not(self, method, wait_seconds=DEFAULT_WAIT_SECONDS):
        WebDriverWait(self.browser, wait_seconds).until_not(method)

    def element_exists(self, locator):
        try:
            self.wait_for_presence(locator)
            return True
        except TimeoutException:
            return False

    def element_does_not_exist(self, locator):
        try:
            self.wait_for_absence(locator)
            return True
        except TimeoutException:
            return False

    def element_does_not_exist_by_id(self, name):
        return self.element_does_not_exist((By.ID, name))

    def element_exists_by_id(self, name):
        return self.element_exists((By.ID, name))

    def element_does_not_exist_by_link_text(self, name):
        return self.element_does_not_exist((By.LINK_TEXT, name))

    def element_exists_by_css(self, name):
        return self.element_exists((By.CSS_SELECTOR, name))

    def on_correct_page(self, pageName):
        return self.element_exists_by_id(pageName)

    def hover_over_resources_dropdown(self):
        resources_dropdown = self.browser.find_element(
            By.ID, "teaching_resources_button"
        )
        hover = ActionChains(self.browser).move_to_element(resources_dropdown)
        hover.perform()

    def go_to_rapid_router_resources_page(self):
        self.hover_over_resources_dropdown()
        self.browser.find_element(
            By.ID, "rapid_router_resources_button"
        ).click()
        from .resources_page import ResourcesPage

        return ResourcesPage(self.browser)

    def is_on_admin_login_page(self):
        return self.on_correct_page("administration_login")

    def is_on_admin_data_page(self):
        return self.on_correct_page("admin_data")

    def is_on_admin_map_page(self):
        return self.on_correct_page("admin_map")

    def is_on_403_forbidden(self):
        return self.on_correct_page("403_forbidden")

    def was_form_invalid(self, formID, error):
        errors = (
            self.browser.find_element(By.ID, formID)
            .find_element(By.CLASS_NAME, "errorlist")
            .text
        )
        return error in errors

    def is_dialog_showing(self):
        time.sleep(FADE_TIME)
        return self.browser.find_element(By.ID, "popup").is_displayed()

    def confirm_dialog(self):
        self.browser.find_element(By.ID, "confirm_button").click()
        time.sleep(FADE_TIME)
        return self

    def cancel_dialog(self):
        self.browser.find_element(By.ID, "cancel_button").click()
        time.sleep(FADE_TIME)
        return self
