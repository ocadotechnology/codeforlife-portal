from typing import Tuple

from common.helpers.generators import generate_access_code
from common.models import Class, Teacher


def generate_details():
    name = "Class %d" % generate_details.next_id
    access_code = generate_access_code()

    generate_details.next_id += 1

    return name, access_code


generate_details.next_id = 1


def create_class_directly(
    teacher_email: str, class_name: str = None
) -> Tuple[Class, str, str]:
    """Generate a class with the details given.

    Args:
        teacher_email (str): The email of the teacher that will own the class.
        class_name (str, optional): The name of the class. Defaults to auto-generated name.

    Returns:
        (class: Class, name: str, access_code: str): A tuple with the class model instance, name and access code.
    """
    name, access_code = generate_details()

    if class_name is not None:
        name = class_name

    teacher = Teacher.objects.get(new_user__email=teacher_email)

    klass = Class.objects.create(name=name, access_code=access_code, teacher=teacher)

    return klass, name, access_code
