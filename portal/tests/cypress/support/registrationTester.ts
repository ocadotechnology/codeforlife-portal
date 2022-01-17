/// <reference types="cypress" />

export function testRegistration(registerFunction, registrationDetails, successful, errorMessage) {
  // log in, check the user is logged in and get the session cookie.
  registerFunction(...registrationDetails);

  if (!successful) {
      cy.get('.errorlist').should('be.visible')
      cy.get('.errorlist').should('have.text', errorMessage)
  }
}
