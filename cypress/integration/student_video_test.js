it ('clicks the link "type"', function (){

    cy.visit('http://localhost:8000')

    cy.contains('Students').click()

    cy.get('[src="/static/portal/img/thumbnail_intro_rr.jpg"]').click()
    
    cy.get('#cboxClose').click()

})