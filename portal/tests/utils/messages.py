def is_message_showing(browser, message):
    return (message in browser.find_element_by_id('messages').text)

def is_email_verified_message_showing(browser):
    return is_message_showing(browser, 'Your email address was successfully verified, please log in.')

def is_teacher_details_updated_message_showing(browser):
    return is_message_showing(browser, 'Your account details have been successfully changed.')

def is_teacher_email_updated_message_showing(browser):
    return is_message_showing(browser, 'Your account details have been successfully changed. Your email will be changed once you have verified it, until then you can still log in with your old email.')

def is_organisation_created_message_showing(browser, name):
    return is_message_showing(browser, "The school or club '%s' has been successfully added." % name)

def is_class_created_message_showing(browser, name):
    return is_message_showing(browser, "The class '%s' has been created successfully." % name)

def is_class_nonempty_message_showing(browser):
    return is_message_showing(browser, "This class still has students, please remove or delete them all before deleting the class.")