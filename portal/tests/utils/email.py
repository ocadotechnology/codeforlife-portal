import string
import re

def follow_verify_email_link(page, email):
    message = str(email.message())

    prefix = '<p>Please go to <a href="'
    i = string.find(message, prefix) + len(prefix)

    suffix = '" rel="nofollow">'
    j = string.find(message, suffix, i)

    page.browser.get(message[i:j])

    return go_to_teach_or_play(page)

def follow_reset_email_link(browser, email):
    message = str(email.body)

    link = re.search("http.+/", message).group(0)

    browser.get(link)

    from portal.tests.pageObjects.registration.password_reset_form_page import PasswordResetPage
    return PasswordResetPage(browser)

def follow_change_email_link(page, email):
    message = str(email.message())

    prefix = 'please go to '
    i = string.find(message, prefix) + len(prefix)

    suffix = ' to verify'
    j = string.find(message, suffix, i)

    page.browser.get(message[i:j])

    return go_to_teach_or_play(page)

def go_to_teach_or_play(page):
    if page.on_correct_page('teach_page'):
        return go_to_teach_page(page.browser)
    else:
        return go_to_play_page(page.browser)

def go_to_play_page(browser):
    from portal.tests.pageObjects.portal.play_page import PlayPage

    return PlayPage(browser)


def go_to_teach_page(browser):
    from portal.tests.pageObjects.portal.teach_page import TeachPage

    return TeachPage(browser)

