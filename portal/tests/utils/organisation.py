def create_organisation(page, password):
    page = page.goToOrganisationPage()
    
    name = 'School %d' % create_organisation.next_id
    postcode = 'Al10 9NE'

    page = page.create_organisation(name, postcode, password)
    create_organisation.next_id += 1

    return page, name, postcode

create_organisation.next_id = 1
