it ('clicks the link "type"', function (){

    cy.visit('http://localhost:8000')

    cy.get('[src="/static/portal/img/twitter.png"]').click()

    cy.visit('http://localhost:8000')

    cy.get('[src="/static/portal/img/facebook.png"]').click()

    cy.visit('http://localhost:8000')

    cy.get('[src="/static/portal/img/google%2B.png"]').click()


})