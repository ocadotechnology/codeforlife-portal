from base_test import BaseTest

from pageObjects.portal.home_page import HomePage

class TestNavigation(BaseTest):
    def test_base(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page = page.goToAboutPage()
        page = page.goToContactPage()
        page = page.goToTermsPage()
        page = page.goToHelpPage()
        page = page.goToPlayPage()
        page = page.goToTeachPage()

    def test_home(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)

        page = page.goToTeacherSignUp().goToHomePage()

    def test_play(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page = page.goToPlayPage()

        page = page.goToTeacherLogin().goToPlayPage()
        page.showSoloLogin()
        page = page.goToTeacherLogin().goToPlayPage()
        page.showSchoolLogin()

        assert page.isCorrectLoginState('school')
        assert page.isCorrectSignupState(False)

        page.showSoloLogin()

        assert page.isCorrectLoginState('solo')
        assert page.isCorrectSignupState(False)

        page.showSchoolLogin()

        assert page.isCorrectLoginState('school')
        assert page.isCorrectSignupState(False)

        page.showSignup()

        assert page.isCorrectLoginState('school')
        assert page.isCorrectSignupState(True)

        page.showSoloLogin()

        assert page.isCorrectLoginState('solo')
        assert page.isCorrectSignupState(True)

        page.showSchoolLogin()

        assert page.isCorrectLoginState('school')
        assert page.isCorrectSignupState(True)

        page.showSoloLogin()
        page = page.goToForgottenPasswordPage().cancel().goToPlayPage()


    def test_teach(self):
        self.browser.get(self.home_url)
        page = HomePage(self.browser)
        page = page.goToTeachPage()

        page = page.goToStudentLoginPage().goToTeachPage()

        page = page.goToForgottenPasswordPage().cancel().goToTeachPage()
