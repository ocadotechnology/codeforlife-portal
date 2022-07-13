from common.tests.utils.classes import generate_details


def create_class(page, teacher_id=None):
    name, _ = generate_details()

    page = page.create_class(name, "False", teacher_id=teacher_id)

    return page, name
