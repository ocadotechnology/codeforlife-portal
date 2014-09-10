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
