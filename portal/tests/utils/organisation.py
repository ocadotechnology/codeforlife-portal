def create_organisation(page, password):
    page = page.goToOrganisationPage()
    name = 'School %d' % create_organisation.next_id
    page = page.create_organisation(name, 'Al10 9NE', password)
    return page, name

create_organisation.next_id = 1
