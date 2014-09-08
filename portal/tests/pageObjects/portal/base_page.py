from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage(object):
    browser = None

    def __init__(self, browser):
        self.browser = browser

    def onCorrectPage(self, pageName):
        try:
            WebDriverWait(self.browser, 1).until(
                EC.presence_of_element_located((By.ID, pageName))
            )
            return True
        except TimeoutException:
            return False

    def goToAboutPage(self):
        self.browser.find_element_by_id('about_button').click()
        return about_page.AboutPage(self.browser)

    def goToContactPage(self):
        self.browser.find_element_by_id('contact_button').click()
        return contact_page.ContactPage(self.browser)

    def goToHelpPage(self):
        self.browser.find_element_by_id('help_button').click()
        return help_and_support_page.HelpPage(self.browser)

    def goToHomePage(self):
        self.browser.find_element_by_id('home_button').find_element_by_tag_name('span').click()
        return home_page.HomePage(self.browser)

    def goToPlayPage(self):
        self.browser.find_element_by_id('play_button').click()
        return play_page.PlayPage(self.browser)

    def goToTeachPage(self):
        self.browser.find_element_by_id('teach_button').click()
        return teach_page.TeachPage(self.browser)

    def goToTermsPage(self):
        self.browser.find_element_by_id('terms_button').click()
        return terms_page.TermsPage(self.browser)

import about_page
import contact_page
import help_and_support_page
import home_page
import play_page
import teach_page
import terms_page
