from django.core import mail

def signup_teacher(page):
    page = page.goToTeachPage()

    page = page.signup('Mr', 'Test', 'Teacher', 'testteacher%d@codeforlife.com' % signup_teacher.next_id, 'Password1', 'Password1')
    signup_teacher.next_id += 1

    page = page.returnToHomePage()

    page = email.follow_verify_email_link(page, mail.outbox[0])

    return page

signup_teacher.next_id = 1

import email