def is_email_verified_message_showing(browser):
    message = 'Your email address was successfully verified, please log in.'
    return (message in browser.find_element_by_id('messages').text)

def is_teacher_details_updated_message_showing(browser):
    message = 'Your account details have been successfully changed.'
    return (message in browser.find_element_by_id('messages').text)

def is_teacher_email_updated_message_showing(browser):
    message = 'Your account details have been successfully changed. Your email will be changed once you have verified it, until then you can still log in with your old email.'
    return (message in browser.find_element_by_id('messages').text)
