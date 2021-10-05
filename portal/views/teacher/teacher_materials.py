from builtins import range
from builtins import str

from aimmo.models import Worksheet
from common.permissions import logged_in_as_teacher
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.urls import reverse_lazy

from portal.strings.kurono_teaching_packs import KURONO_TEACHING_PACKS_BANNER
from portal.strings.materials import MATERIALS_BANNER
from portal.views.teacher.pdfs import PDF_DATA


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def materials(request):

    session_names = [
        "KS1_session_",
        "KS2_session_",
        "Lower_KS3_session_",
        "Intermediate_KS3_session_",
        "Upper_KS3_session_",
    ]
    resource_sheets_names = [
        "KS1_S",
        "KS2_S",
        "Lower_KS3_S",
        "Intermediate_KS3_S",
        "Upper_KS3_S",
    ]
    ks1_sessions = []
    ks2_sessions = []
    lower_ks3_sessions = []
    intermediate_ks3_sessions = []
    upper_ks3_sessions = []
    session_lists = [
        ks1_sessions,
        ks2_sessions,
        lower_ks3_sessions,
        intermediate_ks3_sessions,
        upper_ks3_sessions,
    ]
    ks1_sheets = []
    ks2_sheets = []
    lower_ks3_sheets = []
    intermediate_ks3_sheets = []
    upper_ks3_sheets = []
    resource_sheets_lists = [
        ks1_sheets,
        ks2_sheets,
        lower_ks3_sheets,
        intermediate_ks3_sheets,
        upper_ks3_sheets,
    ]
    ks1_sheets_table = {}
    ks2_sheets_table = {}
    lower_ks3_sheets_table = {}
    intermediate_ks3_sheets_table = {}
    upper_ks3_sheets_table = {}
    resource_sheets_tables = [
        ks1_sheets_table,
        ks2_sheets_table,
        lower_ks3_sheets_table,
        intermediate_ks3_sheets_table,
        upper_ks3_sheets_table,
    ]

    for ks_index, session_name in enumerate(session_names):
        get_session_pdfs(session_name, session_lists[ks_index])
        get_resource_sheets_pdfs(
            session_lists[ks_index],
            resource_sheets_names[ks_index],
            resource_sheets_lists[ks_index],
            resource_sheets_tables[ks_index],
        )
        resource_sheets_tables[ks_index]["content"] = resource_sheets_lists[ks_index]

    return render(
        request,
        "portal/teach/materials.html",
        {
            "ks1_sessions": ks1_sessions,
            "ks1_sheets": ks1_sheets_table,
            "ks2_sessions": ks2_sessions,
            "ks2_sheets": ks2_sheets_table,
            "lower_ks3_sessions": lower_ks3_sessions,
            "lower_ks3_sheets": lower_ks3_sheets_table,
            "intermediate_ks3_sessions": intermediate_ks3_sessions,
            "intermediate_ks3_sheets": intermediate_ks3_sheets_table,
            "upper_ks3_sessions": upper_ks3_sessions,
            "upper_ks3_sheets": upper_ks3_sheets_table,
            "BANNER": MATERIALS_BANNER,
        },
    )


def get_session_pdfs(session_name, session_list):
    session_pdf_exists = True
    session_number = update_session_number_based_on_key_stage(session_name)

    while session_pdf_exists:
        pdf_name = session_name + str(session_number)

        try:
            pdf = PDF_DATA[pdf_name]
            pdf["session_number"] = session_number
            pdf["url_name"] = pdf_name
            session_list.append(pdf)
            session_number += 1
        except KeyError:
            session_pdf_exists = False


def get_resource_sheets_pdfs(
    session_list, resource_sheets_name, resource_sheets_list, resource_sheets_table=None
):
    """
    This function gathers all the resource sheets for each session in the session list. It finds the correct PDFs based
    on the session number and the prefix of the resource sheets name. In addition, if a resource sheets table is
    defined, it will add the starting session index to the dictionary.
    :param session_list: The list of sessions for which this function will gather resource sheets.
    :param resource_sheets_name: The prefix of the name of the required resource sheets' names.
    :param resource_sheets_list: The resource sheets list which is updated to contain the resource sheets.
    :param resource_sheets_table: Optional argument. If defined, it means the data is supposed to be shown in a table
    and requires a starting session index to be able to iterate properly.
    """
    starting_session_index = update_session_number_based_on_key_stage(
        resource_sheets_name
    )
    if resource_sheets_table is not None:
        resource_sheets_table["starting_session_index"] = starting_session_index

    for session_index in range(
        starting_session_index, len(session_list) + starting_session_index
    ):
        resource_pdf_exists = True
        resource_number = 1
        pdfs = []

        while resource_pdf_exists:
            pdf_name = (
                resource_sheets_name + str(session_index) + "_" + str(resource_number)
            )

            try:
                pdf = PDF_DATA[pdf_name]
                pdf["session_number"] = session_index
                pdf["url_name"] = pdf_name
                pdfs.append(pdf)
                resource_number += 1

            except KeyError:
                resource_pdf_exists = False

        resource_sheets_list.append(pdfs)


def update_session_number_based_on_key_stage(key_stage_name):
    """
    Defines the correct starting session index based on which key stage is specified.
    :param key_stage_name: Prefix of the specified key stage's session or resource sheets name.
    :return: Returns the appropriate starting session index.
    """
    DEFAULT_KS_STARTING_SESSION_INDEX = 1
    INTERMEDIATE_KS3_STARTING_SESSION_INDEX = 6
    UPPER_KS3_STARTING_SESSION_INDEX = 11

    if (
        key_stage_name == "Intermediate_KS3_session_"
        or key_stage_name == "Intermediate_KS3_S"
    ):
        session_number = INTERMEDIATE_KS3_STARTING_SESSION_INDEX
    elif key_stage_name == "Upper_KS3_session_" or key_stage_name == "Upper_KS3_S":
        session_number = UPPER_KS3_STARTING_SESSION_INDEX
    else:
        session_number = DEFAULT_KS_STARTING_SESSION_INDEX

    return session_number


@login_required(login_url=reverse_lazy("teacher_login"))
@user_passes_test(logged_in_as_teacher, login_url=reverse_lazy("teacher_login"))
def kurono_teaching_packs(request):
    worksheets = Worksheet.objects.all()
    return render(
        request,
        "portal/teach/kurono_teaching_packs.html",
        {
            "worksheets": worksheets,
            "KURONO_TEACHING_PACKS_BANNER": KURONO_TEACHING_PACKS_BANNER,
        },
    )
