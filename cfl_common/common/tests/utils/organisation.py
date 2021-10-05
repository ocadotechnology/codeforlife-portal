from common.models import Teacher, School


def generate_details(**kwargs):
    name = kwargs.get("name", "School %d" % generate_details.next_id)
    postcode = kwargs.get("postcode", "Al10 9NE")

    generate_details.next_id += 1

    return name, postcode


generate_details.next_id = 1


def create_organisation_directly(teacher_email, **kwargs):
    name, postcode = generate_details(**kwargs)

    school = School.objects.create(
        name=name, postcode=postcode, country="GB", town="", latitude="", longitude=""
    )

    teacher = Teacher.objects.get(new_user__email=teacher_email)
    teacher.school = school
    teacher.is_admin = True
    teacher.save()

    return name, postcode


def join_teacher_to_organisation(teacher_email, org_name, postcode, is_admin=False):
    teacher = Teacher.objects.get(new_user__email=teacher_email)
    school = School.objects.get(name=org_name, postcode=postcode)

    teacher.school = school
    teacher.is_admin = is_admin
    teacher.save()


def create_organisation(page, password):

    name, postcode = generate_details()
    page = page.create_organisation(name, password, postcode)

    return page, name, postcode
