from portal.models import Teacher, School

def generate_details():
    name = 'School %d' % generate_details.next_id
    postcode = 'Al10 9NE'

    generate_details.next_id += 1

    return name, postcode

generate_details.next_id = 1

def create_organisation_directly(teacher_email):
    name, postcode = generate_details()

    school = School.objects.create(
        name = name,
        postcode = postcode,
        town = '',
        latitude = '',
        longitude = '')

    teacher = Teacher.objects.get(user__user__email=teacher_email)
    teacher.school = school
    teacher.is_admin = True
    teacher.save()

    return name, postcode

def create_organisation(page, password):
    page = page.goToOrganisationPage()
    
    name, postcode = generate_details()
    page = page.create_organisation(name, postcode, password)

    return page, name, postcode
