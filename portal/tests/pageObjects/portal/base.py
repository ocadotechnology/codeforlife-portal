from django.conf import settings
from selenium import webdriver

class BasePage(object):
    browser = None

    def __init__(self, browser):
        self.browser = browser

    def goToAboutPage(self):
        self.browser.find_element_by_id('about_button').click()
        return about.AboutPage(self.browser)

    def goToContactPage(self):
        self.browser.find_element_by_id('contact_button').click()
        return contact.ContactPage(self.browser)

    def goToHelpPage(self):
        self.browser.find_element_by_id('help_button').click()
        return help_and_support.HelpPage(self.browser)

    def goToHomePage(self):
        self.browser.find_element_by_id('home_button').click()
        return home.HomePage(self.browser)

    def goToPlayPage(self):
        self.browser.find_element_by_id('play_button').click()
        return play.PlayPage(self.browser)

    def goToTeachPage(self):
        self.browser.find_element_by_id('teach_button').click()
        return teach.TeachPage(self.browser)

    def goToTermsPage(self):
        self.browser.find_element_by_id('terms_button').click()
        return terms.TermsPage(self.browser)

import about
import contact
import help_and_support
import home
import play
import teach
import terms
