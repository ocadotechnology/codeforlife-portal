from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.play.play_base_page import PlayBasePage


class JoinSchoolOrClubPage(PlayBasePage):
    def __init__(self, browser):
        super(JoinSchoolOrClubPage, self).__init__(browser)

        assert self.on_correct_page("play_join_organisation_page")

    def join_a_school_or_club(self, access_code):
        self.browser.find_element(By.ID, "id_access_code").send_keys(access_code)
        self.browser.find_element(By.ID, "request_join_a_school_or_club_button").click()
        assert self.element_exists_by_css(".success")

        return self

    def join_a_school_or_club_failure(self, access_code):
        self.browser.find_element(By.ID, "id_access_code").send_keys(access_code)
        self.browser.find_element(By.ID, "request_join_a_school_or_club_button").click()
        assert not self.element_exists_by_css(".success")

        return self

    def has_join_request_failed(self, error):
        errors = self.browser.find_element(By.ID, "join_class_form").find_element(By.CLASS_NAME, "errorlist").text
        return error in errors

    def revoke_join_request(self):
        self.browser.find_element(By.NAME, "revoke_join_request").click()

        return self
