from common.tests.utils.classes import generate_details


def create_class(page):
    name, _ = generate_details()

    page = page.create_class(name, "False")

    return page, name
