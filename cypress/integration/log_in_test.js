it ('clicks the link "type"', function (){

    cy.visit('http://localhost:8000')

    cy.get('#login_button').click()

    //Teacher login test

    cy.get('#id_login-teacher_email')
        .type('HECK_MECK@email.com')
        .should('have.value', 'HECK_MECK@email.com').click()

    cy.get('#id_login-teacher_password')
        .type('Bayblade7')
        .should('have.value', 'Bayblade7').click()

    cy.get('[name=login_view]').click()


}) 