from builtins import str


def follow_verify_email_link_to_onboarding(page, url):
    page.browser.get(url)

    return go_to_teacher_login_page(page.browser)


def follow_verify_email_link_to_login(page, url, user_type):
    page.browser.get(url)

    if user_type == "teacher":
        return go_to_teacher_login_page(page.browser)
    elif user_type == "independent":
        return go_to_independent_student_login_page(page.browser)


def follow_duplicate_account_link_to_login(page, url, user_type):
    page.browser.get(url)

    if user_type == "teacher":
        return go_to_teacher_login_page(page.browser)
    elif user_type == "independent":
        return go_to_independent_student_login_page(page.browser)


def follow_reset_email_link(browser, link):
    browser.get(link)

    from portal.tests.pageObjects.portal.password_reset_form_page import (
        PasswordResetPage,
    )

    return PasswordResetPage(browser)


def follow_change_email_link_to_dashboard(page, url):
    page.browser.get(url)

    return go_to_teacher_login_page(page.browser)


def follow_change_email_link_to_independent_dashboard(page, url):
    page.browser.get(url)

    return go_to_independent_student_login_page(page.browser)


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
