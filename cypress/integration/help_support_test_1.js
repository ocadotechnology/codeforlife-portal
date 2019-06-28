it ('clicks the link "type"', function (){

    cy.visit('http://localhost:8000')

    cy.get('#help_and_support_button').click()
    
    //Everything incorrect other than email
    cy.get('#id_name')
    .type('1234')
    .should('have.value', '1234').click()

    cy.get('#id_telephone')
        .type('ahahah')
        .should('have.value', 'ahahah').click()

    cy.get('#id_email')
    .type('fake@email.com')
    .should('have.value', 'fake@email.com').click()

    cy.get('#id_message')
    .type(' ')
    .should('have.value', ' ').click()

    cy.contains('Submit').click()

    cy.get('#help_and_support_button').click()
    
    //Incorrect email test
    cy.get('#id_name')
    .type('Mark')
    .should('have.value', 'Mark').click()

    cy.get('#id_telephone')
        .type('12345')
        .should('have.value', '12345').click()

    cy.get('#id_email')
    .type('fakeemail.com')
    .should('have.value', 'fakeemail.com').click()

    cy.get('#id_message')
    .type('ay yuh')
    .should('have.value', 'ay yuh').click()

    cy.contains('Submit').click()

    cy.get('#help_and_support_button').click()

    //successful test

    cy.get('#id_name')
    .type('A')
    .should('have.value', 'A').click()

    cy.get('#id_telephone')
        .type('123456')
        .should('have.value', '123456').click()

    cy.get('#id_email')
    .type('fake@email.com')
    .should('have.value', 'fake@email.com').click()

    cy.get('#id_message')
    .type('Hey yoh')
    .should('have.value', 'Hey yoh').click()

    cy.contains('Submit').click()

})
     