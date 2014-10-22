import re

from portal.models import Teacher, Class
from portal.helpers.generators import generate_access_code

def generate_details():
    name = 'Class %d' % generate_details.next_id
    accesss_code = generate_access_code()

    generate_details.next_id += 1

    return name, accesss_code

generate_details.next_id = 1

def generate_email(name):
    return name.replace(' ','_') + '@codeforlife.com'

def create_class_directly(teacher_email):
    name, accesss_code = generate_details()

    teacher = Teacher.objects.get(user__user__email=teacher_email)

    klass = Class.objects.create(
        name=name,
        access_code=accesss_code,
        teacher=teacher)

    return name, accesss_code

def create_class(page):
    page = page.go_to_classes_page()

    name, _ = generate_details()

    page = page.create_class(name, 'False')

    accesss_code = re.search('([A-Z]{2}[0-9]{3})\)$', page.browser.find_element_by_id('class_header').text).group(1)
    
    return page, name, accesss_code

def transfer_class(page, teacher_index):
    return page.transfer_class().select_teacher_by_index(teacher_index).move()

def move_students(page, class_index):
    return page.move_students().select_class_by_index(class_index).move().move()

def dismiss_students(page):
    page = page.dismiss_students()

    emails = []

    for name in page.get_list_of_students():
        email = generate_email(name)
        emails.append(email)
        
        page = page.enter_email(name, email)

    page = page.dismiss()

    return page, emails