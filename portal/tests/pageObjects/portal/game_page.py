from __future__ import print_function

import os
import time
from builtins import str

from hamcrest import assert_that, equal_to, contains_string
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from portal.tests.pageObjects.portal.base_page import BasePage


class GamePage(BasePage):
    def __init__(self, browser):
        super(GamePage, self).__init__(browser)

        assert self.on_correct_page("game_page")

        self._dismiss_initial_dialog()

    def _dismiss_initial_dialog(self):
        self.dismiss_dialog("play_button")
        return self

    def dismiss_dialog(self, button_id):
        self.wait_for_element_to_be_clickable((By.ID, button_id))
        self.browser.find_element(By.ID, button_id).click()
        self.wait_for_element_to_be_invisible((By.ID, button_id))

    def load_solution(self, workspace_id):
        self.browser.find_element(By.ID, "load_tab").click()
        selector = "#loadWorkspaceTable tr[value='" + str(workspace_id) + "']"
        self.wait_for_element_to_be_clickable((By.CSS_SELECTOR, selector))
        self.browser.find_element(By.CSS_SELECTOR, selector).click()
        self.browser.find_element(By.ID, "loadWorkspace").click()
        time.sleep(1)
        return self

    def clear(self):
        self.browser.find_element(By.ID, "clear_tab").click()
        return self

    def try_again(self):
        self.dismiss_dialog("try_again_button")
        return self

    def step(self):
        self.browser.find_element(By.ID, "step_tab").click()
        return self

    def assert_is_green_light(self, traffic_light_index):
        self._assert_light_is_on(traffic_light_index, "green")

    def assert_is_red_light(self, traffic_light_index):
        self._assert_light_is_on(traffic_light_index, "red")

    def _assert_light_is_on(self, traffic_light_index, colour):
        image = self.browser.find_element(By.ID, "trafficLight_%s_%s" % (traffic_light_index, colour))

        assert_that(image.get_attribute("opacity"), equal_to("1"))

    def run_program(self, wait_for_element_id="algorithmScore"):
        self.browser.find_element(By.ID, "fast_tab").click()

        try:
            self.wait_for_element_to_be_clickable((By.ID, wait_for_element_id), 45)
        except TimeoutException as e:
            import time

            millis = int(round(time.time() * 1000))
            screenshot_filename = "/tmp/game_tests_%s-%s.png" % (os.getenv("BUILD_NUMBER", "nonumber"), str(millis))
            print("Saved screenshot to " + screenshot_filename)
            self.browser.get_screenshot_as_file(screenshot_filename)
            raise e

        return self

    def run_crashing_program(self):
        return self._run_failing_program("What went wrong")

    def run_program_that_runs_out_of_instructions(self):
        return self._run_failing_program("The van ran out of instructions before it reached a destination.")

    def _run_failing_program(self, text):
        self.run_program("try_again_button")
        error_message = self.browser.find_element(By.ID, "myModal-lead").text
        assert_that(error_message, contains_string(text))
        return self

    def _assert_score(self, element_id, score):
        route_score = self.browser.find_element(By.ID, element_id).text
        assert_that(route_score, equal_to(score))
        return self

    def assert_route_score(self, score):
        return self._assert_score("routeScore", score)

    def assert_algorithm_score(self, score):
        return self._assert_score("algorithmScore", score)
