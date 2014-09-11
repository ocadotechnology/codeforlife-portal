from play_base_page import PlayBasePage

class PlayAccountPage(PlayBasePage):
    def __init__(self, browser):
        super(PlayAccountPage, self).__init__(browser)

        assert self.on_correct_page('play_account_page')

    def change_details(self, details):
        for field, value in details.items():
            self.browser.find_element_by_id('id_' + field).clear()
            self.browser.find_element_by_id('id_' + field).send_keys(value)

        self.browser.find_element_by_id('update_button').click()

        if self.on_correct_page('play_dashboard_page'):
            return dashboard_page.PlayDashboardPage(self.browser)
        else:
            return self

import dashboard_page
