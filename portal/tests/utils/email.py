import string

def follow_verify_email_link(page, email):
    message = str(email.message())

    prefix = '<p>Please go to <a href="'
    i = string.find(message, prefix) + len(prefix)

    suffix = '" rel="nofollow">'
    j = string.find(message, suffix, i)

    page.browser.get(message[i:j])

    return pageObjects.portal.teach_page.TeachPage(page.browser)

def follow_change_email_link(page, email):
    message = str(email.message())

    prefix = 'please go to '
    i = string.find(message, prefix) + len(prefix)

    suffix = ' to verify'
    j = string.find(message, suffix, i)

    page.browser.get(message[i:j])

    return pageObjects.portal.teach_page.TeachPage(page.browser)

import pageObjects.portal.teach_page