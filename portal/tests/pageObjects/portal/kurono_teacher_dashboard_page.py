from __future__ import absolute_import

from .base_page import BasePage


class KuronoTeacherDashboardPage(BasePage):
    def __init__(self, browser):
        super(KuronoTeacherDashboardPage, self).__init__(browser)

        assert self.on_correct_page("kurono_teacher_dashboard_page")

    def create_game(self, class_id):
        self._click_add_game_dropdown()

        self.browser.find_element_by_id(f"class_{class_id}").click()

        return self

    def change_game_worksheet(self, worksheet_id):
        self._click_change_worksheet_dropdown()

        self.browser.find_element_by_id(f"worksheet_{worksheet_id}").click()

        self.confirm_dialog()

        return self

    def delete_games(self, game_ids):
        # Tick checkboxes
        for game_id in game_ids:
            self.browser.find_element_by_xpath(
                f"//input[@name='game_ids' and @value='{game_id}']"
            ).click()

        # Click delete
        self.browser.find_element_by_xpath(
            '//*[@id="games-table"]/tbody/tr[4]/td[2]/div/a'
        ).click()

        self.confirm_dialog()

        return self

    def _click_change_worksheet_confirm_button(self):
        self.browser.find_element_by_id("confirm_button").click()

    def _click_add_game_dropdown(self):
        self.browser.find_element_by_id("add_class_dropdown").click()

    def _click_change_worksheet_dropdown(self):
        self.browser.find_element_by_id("worksheets_dropdown").click()
