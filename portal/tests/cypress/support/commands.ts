// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

const teacherUsername = 'alberteinstein@codeforlife.com'
const teacherPassword = 'Password1'
const studentUsername = 'Leonardo'
const studentAccessCode = 'AB123'
const studentPassword = 'Password1'
const independentStudentUsername = 'indy'
const independentStudentPassword = 'Password1'

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

Cypress.Commands.add('loginAsTeacher', () => {
  cy.request('/login/teacher/')
  cy.getCookie('csrftoken').then(csrfToken => {
    cy.request({
      method: 'POST',
      url: '/login/teacher/',
      failOnStatusCode: true,
      form: true,
      body: {
        'auth-username': teacherUsername,
        'auth-password': teacherPassword,
        csrfmiddlewaretoken: csrfToken.value,
        'teacher_login_view-current_step': 'auth'
      }
    })
    cy.visit('/')
  })
})

Cypress.Commands.add('loginAsStudent', () => {
  cy.request(`/login/student/${studentAccessCode}/`)
  cy.getCookie('csrftoken').then(csrfToken => {
    cy.request({
      method: 'POST',
      url: `/login/student/${studentAccessCode}/`,
      failOnStatusCode: true,
      form: true,
      body: {
        username: studentUsername,
        password: studentPassword,
        csrfmiddlewaretoken: csrfToken.value
      }
    })
    cy.visit('/')
  })
})

Cypress.Commands.add('loginAsIndependentStudent', () => {
  cy.request('/login/independent/')
  cy.getCookie('csrftoken').then(csrfToken => {
    cy.request({
      method: 'POST',
      url: '/login/independent/',
      failOnStatusCode: true,
      form: true,
      body: {
        username: independentStudentUsername,
        password: independentStudentPassword,
        csrfmiddlewaretoken: csrfToken.value
      }
    })
    cy.visit('/')
  })
})
