from common.models import School, Teacher


def generate_details(**kwargs):
    name = kwargs.get("name", "School %d" % generate_details.next_id)

    generate_details.next_id += 1

    return name


generate_details.next_id = 1


def create_organisation_directly(teacher_email, **kwargs):
    name = generate_details(**kwargs)

    school = School.objects.create(name=name, country="GB")

    teacher = Teacher.objects.get(new_user__email=teacher_email)
    teacher.school = school
    teacher.is_admin = True
    teacher.save()

    return school


def join_teacher_to_organisation(teacher_email, org_name, is_admin=False):
    teacher = Teacher.objects.get(new_user__email=teacher_email)
    school = School.objects.get(name=org_name)

    teacher.school = school
    teacher.is_admin = is_admin
    teacher.save()


def create_organisation(page, password):
    name = generate_details()
    page = page.create_organisation(name, password)

    return page, name
