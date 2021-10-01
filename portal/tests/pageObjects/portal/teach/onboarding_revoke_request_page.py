from __future__ import absolute_import

from .teach_base_page import TeachBasePage


class OnboardingRevokeRequestPage(TeachBasePage):
    def __init__(self, browser):
        super(OnboardingRevokeRequestPage, self).__init__(browser)

        assert self.on_correct_page("onboarding_revoke_request_page")

    def check_organisation_name(self, name, postcode):
        text = "You have a pending request to join %s, %s" % (name, postcode)
        return text in self.browser.find_element_by_tag_name("body").text

    def revoke_join(self):
        self.browser.find_element_by_name("revoke_join_request").click()
        import portal.tests.pageObjects.portal.teach.onboarding_organisation_page as onboarding_organisation_page

        return onboarding_organisation_page.OnboardingOrganisationPage(self.browser)
