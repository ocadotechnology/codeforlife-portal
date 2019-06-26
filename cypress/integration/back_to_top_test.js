it ('clicks the link "type"', function (){
    
    cy.visit('http://localhost:8000')

    cy.get('#back_to_top_button').click()
    
    cy.url().should('include', '#top')

})