import re
from builtins import str


def follow_verify_email_link_to_onboarding(page, email):
    _follow_verify_email_link(page, email)

    return go_to_teacher_login_page(page.browser)


def follow_verify_email_link_to_teacher_dashboard(page, email):
    _follow_verify_email_link(page, email)

    return go_to_teacher_dashboard_page(page.browser)


def follow_verify_email_link_to_login(page, email, user_type):
    _follow_verify_email_link(page, email)

    if user_type == "teacher":
        return go_to_teacher_login_page(page.browser)
    elif user_type == "independent":
        return go_to_independent_student_login_page(page.browser)


def follow_duplicate_account_link_to_login(page, email, user_type):
    _follow_duplicate_account_email_link(page, email)

    if user_type == "teacher":
        return go_to_teacher_login_page(page.browser)
    elif user_type == "independent":
        return go_to_independent_student_login_page(page.browser)


def _follow_verify_email_link(page, email):
    message = str(email.message())
    prefix = '<p>Please go to <a href="'
    i = str.find(message, prefix) + len(prefix)
    suffix = '" rel="nofollow">'
    j = str.find(message, suffix, i)
    page.browser.get(message[i:j])


def _follow_duplicate_account_email_link(page, email):
    message = str(email.message())
    prefix = 'please login: <a href="'
    i = str.find(message, prefix) + len(prefix)
    suffix = '" rel="nofollow">'
    j = str.find(message, suffix, i)
    page.browser.get(message[i:j])


def follow_reset_email_link(browser, email):
    message = str(email.body)

    link = re.search("http.+/", message).group(0)

    browser.get(link)

    from portal.tests.pageObjects.portal.password_reset_form_page import (
        PasswordResetPage,
    )

    return PasswordResetPage(browser)


def follow_change_email_link_to_dashboard(page, email):
    _follow_change_email_link(page, email)

    return go_to_teacher_login_page(page.browser)


def follow_change_email_link_to_independent_dashboard(page, email):
    _follow_change_email_link(page, email)

    return go_to_independent_student_login_page(page.browser)


def _follow_change_email_link(page, email):
    message = str(email.message())
    prefix = "please go to "
    i = str.find(message, prefix) + len(prefix)
    suffix = " to verify"
    j = str.find(message, suffix, i)
    page.browser.get(message[i:j])


def go_to_teacher_login_page(browser):
    from portal.tests.pageObjects.portal.teacher_login_page import TeacherLoginPage

    return TeacherLoginPage(browser)


def go_to_teacher_dashboard_page(browser):
    from portal.tests.pageObjects.portal.teach.dashboard_page import TeachDashboardPage

    return TeachDashboardPage(browser)


def go_to_independent_student_login_page(browser):
    from portal.tests.pageObjects.portal.independent_login_page import (
        IndependentStudentLoginPage,
    )

    return IndependentStudentLoginPage(browser)
