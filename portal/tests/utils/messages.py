def is_email_verified_message_showing(browser):
    message = 'Your email address was successfully verified, please log in.'
    return (message in browser.find_element_by_id('messages').text)

def is_teacher_details_updated_message_showing(browser):
    message = 'Your account details have been successfully changed.'
    return (message in browser.find_element_by_id('messages').text)
