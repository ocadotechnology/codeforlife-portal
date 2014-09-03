def is_email_verified_message_showing(browser):
    message = 'Your email address was successfully verified, please log in.'
    return (message in browser.find_element_by_id('messages').text)