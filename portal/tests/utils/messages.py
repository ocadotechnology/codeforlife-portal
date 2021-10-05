def is_message_showing(browser, message):
    return message in browser.find_element_by_id("messages").text


def is_email_verified_message_showing(browser):
    return is_message_showing(
        browser, "Your email address was successfully verified, please log in."
    )


def is_teacher_details_updated_message_showing(browser):
    return is_message_showing(
        browser, "Your account details have been successfully changed."
    )


def is_student_details_updated_message_showing(browser):
    return is_message_showing(
        browser, "Your account details have been changed successfully."
    )


def is_indep_student_join_request_received_message_showing(browser):
    return is_message_showing(
        browser, "Your request to join a school has been received successfully."
    )


def is_indep_student_join_request_revoked_message_showing(browser):
    return is_message_showing(
        browser, "Your request to join a school has been cancelled successfully."
    )


def is_email_updated_message_showing(browser):
    return is_message_showing(
        browser,
        "Your email will be changed once you have verified it, until then "
        "you can still log in with your old email.",
    )


def is_password_updated_message_showing(browser):
    return is_message_showing(
        browser,
        "Please login using your new password.",
    )


def is_organisation_created_message_showing(browser, name):
    return is_message_showing(
        browser, "The school or club '%s' has been successfully added." % name
    )


def is_class_created_message_showing(browser, name):
    return is_message_showing(
        browser, "The class '%s' has been created successfully." % name
    )


def is_class_nonempty_message_showing(browser):
    return is_message_showing(
        browser,
        "This class still has students, please remove or delete them all before "
        "deleting the class.",
    )


def is_contact_message_sent_message_showing(browser):
    return is_message_showing(browser, "Your message was sent successfully.")
