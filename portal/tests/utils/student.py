from django.core import mail

from portal.models import Class, Student
from portal.helpers.generators import generate_password

def generate_school_details():
    name = 'Student %d' % generate_school_details.next_id
    password = 'Password1'

    generate_school_details.next_id += 1

    return name, password

generate_school_details.next_id = 1

def create_school_student_directly(access_code):
    name, password = generate_school_details()

    klass = Class.objects.get(access_code=access_code)
    student = Student.objects.schoolFactory(klass, name, password)

    return name, password

def create_school_student(page):
    name, _ = generate_school_details()

    page = page.type_student_name(name).create_students()

    password = page.extract_password(name)

    page = page.return_to_class()

    return page, name, password

def create_many_school_students(page, n):
    names = ['' for i in range(n)]
    passwords = ['' for i in range(n)]

    for i in range(n):
        names[i], _ = generate_school_details()
        page = page.type_student_name(names[i])

    page = page.create_students()

    for i in range(n):
        passwords[i] = page.extract_password(names[i])

    page = page.return_to_class()

    return page, names, passwords

def generate_solo_details():
    name = 'Student %d' % generate_solo_details.next_id
    username = 'Student user %d' % generate_solo_details.next_id
    email_address = 'Student%d@codeforlife.com' % generate_solo_details.next_id
    password = 'Password1'

    generate_solo_details.next_id += 1

    return name, username, email_address, password

generate_solo_details.next_id = 1

def create_solo_student(page):
    page = page.go_to_play_page()

    name, username, email_address, password = generate_solo_details()
    page = page.solo_signup(name, username, email_address, password, password)
    
    page = page.return_to_home_page()

    page = email.follow_verify_email_link(page, mail.outbox[0])
    mail.outbox = []

    return page, name, username, email_address, password

import email
