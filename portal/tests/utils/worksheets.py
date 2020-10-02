from typing import Tuple

from aimmo.models import Worksheet


def generate_details():
    name = "Worksheet %d" % generate_details.next_id
    era = 1
    starter_code = "Test code"

    generate_details.next_id += 1

    return name, era, starter_code


generate_details.next_id = 1


def create_worksheet_directly() -> Tuple[Worksheet, str, int, str]:
    """Generate a Worksheet.

    Returns:
        (worksheet: Worksheet, name: str, era: int, starter_code: str): A tuple with
        the worksheet instance, its name, era and starter code.
    """
    name, era, starter_code = generate_details()

    worksheet = Worksheet.objects.create(name=name, era=era, starter_code=starter_code)

    return worksheet, name, era, starter_code
