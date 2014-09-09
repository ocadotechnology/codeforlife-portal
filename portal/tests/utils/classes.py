import re

def generate_details():
    name = 'Class %d' % generate_details.next_id

    generate_details.next_id += 1

    return name

generate_details.next_id = 1

def create_class(page):
    page = page.goToClassesPage()

    name = generate_details()

    page = page.create_class(name, 'False')

    accesss_code = re.search('([A-Z]{2}[0-9]{3})\)$', page.browser.find_element_by_id('class_header').text).group(1)
    
    return page, name, accesss_code
