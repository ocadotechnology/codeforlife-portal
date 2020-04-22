/// <reference types="cypress" />

/**
 * This test goes through a longer user story
 * trying to do almost everything a typical user would do.
 */
export const smokeTest = () => {
  cy.visit('/')

  cy.log('go to Register page')
  cy.get('#signup_button_fake').click()
  cy.get('[data-cy=teacher_signup_title]').should('be.visible')
  cy.get('[data-cy=teacher_signup_title]').should("have.text", "Register as a teacher")
  cy.get('[data-cy=independent_signup_title]').should('be.visible')
  cy.get('[data-cy=independent_signup_title]').should("have.text", "Register as an independent student")

  cy.log('go to Login page')
  cy.get('#login_button').click()
  cy.get('[data-cy=teacher_login_title]').should('be.visible')
  cy.get('[data-cy=teacher_login_title]').should("have.text", "Log in as a teacher")
  cy.get('[data-cy=student_login_title]').should('be.visible')
  cy.get('[data-cy=student_login_title]').should("have.text", "Log in as a student")

  cy.get('[data-cy=independent_login_title]').should('not.be.visible')
  cy.get('#switchToIndependentStudent').click()
  cy.get('[data-cy=student_login_title]').should('not.be.visible')
  cy.get('[data-cy=independent_login_title]').should('be.visible')
  cy.get('[data-cy=independent_login_title]').should("have.text", "Log in as an independent student")
}