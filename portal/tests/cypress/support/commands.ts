// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

Cypress.Commands.add('loginAsSuperuser', (username, password) => {
  cy.visit('/login/teacher/')

  cy.log('go to Teacher Login page')
  cy.get('#id_auth-username').type(username)
  cy.get('#id_auth-password').type(password)
  cy.get('.button--login').click()
})

Cypress.Commands.add('changeAdminPassword', (oldPassword, newPassword) => {
  cy.get('#id_old_password').type(oldPassword)
  cy.get('#id_new_password1').type(newPassword)
  cy.get('#id_new_password2').type(newPassword)
  cy.get('[type=submit]').click()
})

Cypress.Commands.add('deleteUser', (username) => {
  cy.get('[href="/administration/auth/user/"]').contains('Users').click()
  cy.get('a').contains(username).click()
  cy.get('.deletelink').contains('Delete').click()
  cy.get('[type=submit]').contains("Yes, I'm sure").click()
})
