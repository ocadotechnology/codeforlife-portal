def create_class(page):
    page = page.goToClassesPage()
    name = 'Class %d' % create_class.next_id
    page = page.create_class(name, 'False')
    return page, name

create_class.next_id = 1