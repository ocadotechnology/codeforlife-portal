from django.core import mail

from django.contrib.auth.models import User
from portal.models import UserProfile, Teacher

def generate_details():
    title = 'Mr'
    first_name = 'Test'
    last_name = 'Teacher'
    email_address = 'testteacher%d@codeforlife.com' % generate_details.next_id
    password = 'Password1'

    generate_details.next_id += 1

    return title, first_name, last_name, email_address, password

generate_details.next_id = 1

def signup_teacher(page):
    page = page.goToTeachPage()

    title, first_name, last_name, email_address, password = generate_details()
    page = page.signup(title, first_name, last_name, email_address, password, password)
    
    page = page.returnToHomePage()

    page = email.follow_verify_email_link(page, mail.outbox[0])
    mail.outbox = []

    return page, email_address, password

import email