// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --

const username = 'alberteinstein@codeforlife.com'
const password = 'Password1'
const game_name = 'Cypress test game'
const user_id = 2
const class_id = 1
const worksheet_id = 1
const student_username = 'Leonardo'
const student_access_code = 'AB123'

Cypress.Commands.add('loginAsSuperuser', (username, password) => {
  cy.visit('/administration')

  cy.log('go to Admin Login page')
  cy.get('#id_username').type(username)
  cy.get('#id_password').type(password)
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


//
//
// -- This is a child command --
// Cypress.Commands.add("drag", { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add("dismiss", { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite("visit", (originalFn, url, options) => { ... })
