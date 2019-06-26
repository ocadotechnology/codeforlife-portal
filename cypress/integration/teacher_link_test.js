it ('clicks the link "type"', function (){
    cy.visit('http://localhost:8000')

    cy.contains('Teachers').click()
    cy.contains('Students').click()
    cy.contains('Register now').click()
    
    cy.url()
        .should('include', '/register_form')

    cy.get('#id_teacher_signup-teacher_first_name')
        .type('A')
        .should('have.value', 'A').click()
    
    cy.get('#id_teacher_signup-teacher_last_name')
        .type('B')
        .should('have.value', 'B').click()

   cy.get('#id_teacher_signup-newsletter_ticked').click()

   cy.get('#id_teacher_signup-teacher_password')
    .type('G2ih#7RS')
    .should('have.value', 'G2ih#7RS')

    cy.get('#id_teacher_signup-teacher_confirm_password')
        .type('G2ih#7RS')
        .should('have.value', 'G2ih#7RS')

    cy.get('#id_teacher_signup-teacher_email')
        .type('fake@email.com')
        .should('have.value', 'fake@email.com')

        cy.get('[name=teacher_signup]').click()


})
     