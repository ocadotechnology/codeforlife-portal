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