from pathlib import Path

from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.base_page import BasePage


class TeachBasePage(BasePage):
    def __init__(self, browser):
        super(TeachBasePage, self).__init__(browser)

    def logout(self):
        self.browser.find_element(By.ID, "logout_menu").click()

        self.browser.find_element(By.ID, "logout_button").click()
        from portal.tests.pageObjects.portal.home_page import HomePage

        return HomePage(self.browser)

    def import_students_from_csv(self, filename):
        self.browser.execute_script(
            """
            $(document).ready(function () {
                const fileInput = $('<input>').attr({
                    type: 'file'
                })
                fileInput.on('change', studentsCsvChange('#id_names'))
                $('body').append(fileInput);
            })
        """
        )
        self.browser.find_element(By.XPATH, "/html/body/input").send_keys(
            str((Path(__file__).parents[3] / "data" / filename).resolve())
        )

        return self

    def get_students_input_value(self):
        return self.browser.find_element(By.ID, "id_names").get_attribute("value")
