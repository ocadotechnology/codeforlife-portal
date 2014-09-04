from django.core import mail

def signup_teacher(page):
    page = page.goToTeachPage()

    email_address = 'testteacher%d@codeforlife.com' % signup_teacher.next_id
    password = 'Password1'

    page = page.signup('Mr', 'Test', 'Teacher', email_address, password, password)
    signup_teacher.next_id += 1

    page = page.returnToHomePage()

    page = email.follow_verify_email_link(page, mail.outbox[0])
    mail.outbox = []

    return page, email_address, password

signup_teacher.next_id = 1

import email