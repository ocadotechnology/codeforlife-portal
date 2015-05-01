from django.core import mail

from portal.models import Teacher

def generate_details(**kwargs):
    title = kwargs.get('title','Mr')
    first_name = kwargs.get('first_name', 'Test')
    last_name = kwargs.get('last_name', 'Teacher')
    email_address = kwargs.get('email_address', 'testteacher%d@codeforlife.com' % generate_details.next_id)
    password = kwargs.get('password', 'Password1')

    generate_details.next_id += 1

    return title, first_name, last_name, email_address, password

generate_details.next_id = 1

def signup_teacher_directly(**kwargs):
    title, first_name, last_name, email_address, password = generate_details(**kwargs)
    teacher = Teacher.objects.factory(title, first_name, last_name, email_address, password)
    teacher.user.awaiting_email_verification = False
    teacher.user.save()
    return email_address, password

def signup_teacher(page):
    page = page.go_to_teach_page()

    title, first_name, last_name, email_address, password = generate_details()
    page = page.signup(title, first_name, last_name, email_address, password, password)
    
    page = page.return_to_home_page()

    page = email.follow_verify_email_link(page, mail.outbox[0])
    mail.outbox = []

    return page, email_address, password

#import email