from django import template
from django.template.defaultfilters import floatformat

register = template.Library()


@register.filter(name="tableformat")
def tableformat(entry):

    if entry is None:
        return "-"
    elif is_numerical(entry):
        return floatformat(entry, -2)
    else:
        return entry


def is_numerical(str):
    try:
        float(str)
        return True
    except (ValueError, TypeError):
        return False


@register.inclusion_tag("portal/partials/resource_sheets_table.html")
def resource_sheets_table(table):
    """
    This function takes in a dictionary which mirrors the table of resource sheets for a key stage section.
    The dictionary has a starting session index, and the actual table content. The table content is a 2D list:
    a list of sessions, each holding a list of resource sheets.
    Some sessions have more resource sheets than others, as such the table has some rows which contain less columns.
    The lengthen_list function is called to add empty columns to the smaller rows.
    :param table: A dictionary containing a starting session index (integer) and the content of the table (2D list)
    :return: A dictionary containing the table with all rows now of the same length, and the starting session index.
    """
    table_content = table["content"]
    max_count = len(max(table_content, key=len))
    return {
        "table": [lengthen_list(max_count, column) for column in table_content],
        "starting_session_index": table["starting_session_index"],
    }


def lengthen_list(length, list):
    return list + [[]] * (length - len(list))
