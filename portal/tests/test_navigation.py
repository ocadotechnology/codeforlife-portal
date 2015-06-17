from base_test import BaseTest

from pageObjects.portal.home_page import HomePage

class TestNavigation(BaseTest):
    def test_base(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page = page.go_to_about_page()
        page = page.go_to_contact_page()
        page = page.go_to_terms_page()
        page = page.go_to_help_page()
        page = page.go_to_play_page()
        page = page.go_to_teach_page()

    def test_home(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)

        page = page.go_to_teacher_sign_up().go_to_home_page()

    def test_play(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page = page.go_to_play_page()

        page = page.go_to_teacher_login().go_to_play_page()
        page.show_solo_login()
        page = page.go_to_teacher_login().go_to_play_page()
        page.show_school_login()

        assert page.is_correct_login_state('school')
        assert page.is_correct_signup_state(False)

        page.show_solo_login()

        assert page.is_correct_login_state('solo')
        assert page.is_correct_signup_state(False)

        page.show_school_login()

        assert page.is_correct_login_state('school')
        assert page.is_correct_signup_state(False)

        page.show_signup()

        assert page.is_correct_login_state('school')
        assert page.is_correct_signup_state(True)

        page.show_solo_login()

        assert page.is_correct_login_state('solo')
        assert page.is_correct_signup_state(True)

        page.show_school_login()

        assert page.is_correct_login_state('school')
        assert page.is_correct_signup_state(True)

        page.show_solo_login()
        page = page.go_to_forgotten_password_page().cancel().go_to_play_page()


    def test_teach(self):
        self.browser.get(self.live_server_url)
        page = HomePage(self.browser)
        page = page.go_to_teach_page()

        page = page.go_to_student_login_page().go_to_teach_page()

        page = page.go_to_forgotten_password_page().cancel().go_to_teach_page()
