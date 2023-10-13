from __future__ import absolute_import

from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.play.join_school_or_club_page import JoinSchoolOrClubPage
from .play_base_page import PlayBasePage


class PlayDashboardPage(PlayBasePage):
    def __init__(self, browser):
        super(PlayDashboardPage, self).__init__(browser)

        assert self.on_correct_page("play_dashboard_page")

    def go_to_join_a_school_or_club_page(self):
        self.browser.find_element(By.ID, "student_join_school_link").click()

        return JoinSchoolOrClubPage(self.browser)
