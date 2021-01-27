from aimmo.models import Worksheet


def generate_details():
    name = f"Worksheet {generate_details.next_id}"
    era = 1
    starter_code = "Test code"

    generate_details.next_id += 1

    return name, era, starter_code


generate_details.next_id = 1


def create_worksheet_directly(id=None) -> Worksheet:
    """Generate a Worksheet. The Worksheet can be generated with a specific ID if
    wanted.

    Args:
        id (int) (optional): The desired ID of the worksheet, if specified.

    Returns:
        worksheet: Worksheet: The worksheet model instance.
    """
    name, era, starter_code = generate_details()

    if id:
        worksheet = Worksheet.objects.create(
            id=id, name=name, era=era, starter_code=starter_code
        )
    else:
        worksheet = Worksheet.objects.create(
            name=name, era=era, starter_code=starter_code
        )

    return worksheet
