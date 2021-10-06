from __future__ import absolute_import

from .teach_base_page import TeachBasePage


class TeachMoveClassesPage(TeachBasePage):
    def __init__(self, browser):
        super(TeachMoveClassesPage, self).__init__(browser)

        assert self.on_correct_page("move_all_classes_page")

    def move_and_kick(self):
        self.browser.find_element_by_id("move_classes_button").click()
        import portal.tests.pageObjects.portal.teach.dashboard_page as dashboard_page

        return dashboard_page.TeachDashboardPage(self.browser)

    def move_and_leave(self):
        self.browser.find_element_by_id("move_classes_button").click()
        import portal.tests.pageObjects.portal.teach.onboarding_organisation_page as onboarding_organisation_page

        return onboarding_organisation_page.OnboardingOrganisationPage(self.browser)
