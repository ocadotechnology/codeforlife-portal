from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage(object):
    browser = None

    def __init__(self, browser):
        self.browser = browser

    def wait_for_element(self, method):
        WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located(method)
        )

    def wait_for_element_by_id(self, name):
        WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.ID, name))
        )

    def wait_for_element_by_xpath(self, name):
        WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.XPATH, name))
        )

    def element_exists(self, method):
        try:
            self.wait_for_element(method)
            return True
        except TimeoutException:
            return False

    def element_exists_by_id(self, name):
        return self.element_exists((By.ID, name))

    def element_exists_by_xpath(self, path):
        return self.element_exists((By.XPATH, path))

    def on_correct_page(self, pageName):
        return self.element_exists_by_id(pageName)

    def go_to_about_page(self):
        self.browser.find_element_by_id('about_button').click()
        return about_page.AboutPage(self.browser)

    def go_to_contact_page(self):
        self.browser.find_element_by_id('contact_button').click()
        return contact_page.ContactPage(self.browser)

    def go_to_help_page(self):
        self.browser.find_element_by_id('help_button').click()
        return help_and_support_page.HelpPage(self.browser)

    def go_to_home_page(self):
        self.browser.find_element_by_id('home_button').find_element_by_tag_name('span').click()
        return home_page.HomePage(self.browser)

    def go_to_play_page(self):
        self.browser.find_element_by_id('play_button').click()
        return play_page.PlayPage(self.browser)

    def go_to_teach_page(self):
        self.browser.find_element_by_id('teach_button').click()
        return teach_page.TeachPage(self.browser)

    def go_to_terms_page(self):
        self.browser.find_element_by_id('terms_button').click()
        return terms_page.TermsPage(self.browser)

import about_page
import contact_page
import help_and_support_page
import home_page
import play_page
import teach_page
import terms_page
