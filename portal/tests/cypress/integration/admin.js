/// <reference types="cypress" />
/**
 * Checks that the admin password policy is implemented properly.
 * Checks both when creating a new user, and when changing one's own password.
 * Cleanup includes deleting the test user created for this test.
 */
export const adminPasswordPolicyTest = () => {
  const ADMIN_PASSWORD_TOO_WEAK_MESSAGE = `
Password is too weak. Please choose a password that's at least 14 characters long,
contains at least one lowercase letter, one uppercase letter, one digit and
one special character.
`

  // Login as main superuser
  cy.loginAsSuperuser("codeforlife-portal@ocado.com", "abc123")

  cy.wait(2000)

  // Go to admin site
  cy.visit("administration/")

  // Go to user list
  cy.get('[href="/administration/auth/user/add/"]').click()

  // Try adding a user with a weak password
  cy.get('#id_username').type('testadmin')
  cy.get('#id_password1').type('weak')
  cy.get('#id_password2').type('weak')
  cy.get('[name="_save"]').click()

  cy.get('.errorlist').should('be.visible')
  cy.get('.errorlist').should('have.text', ADMIN_PASSWORD_TOO_WEAK_MESSAGE)

  // Add test user successfully
  cy.get('#id_password1').type('ThisIsAStr0ngPassw0rd!')
  cy.get('#id_password2').type('ThisIsAStr0ngPassw0rd!')
  cy.get('[name="_save"]').click()

  // Go to password change page
  cy.get('[href="/administration/password_change/"]').click()

  // Try changing password to a weak password
  cy.changeAdminPassword('abc123', 'weak')

  cy.get('.errorlist').should('be.visible')
  cy.get('.errorlist').should('have.text', ADMIN_PASSWORD_TOO_WEAK_MESSAGE)

  // Back to admin home
  cy.get('[href="/administration/"]').contains("Home").click()

  // Delete the test user
  cy.deleteUser('testadmin')

  // Logout
  cy.get('[action="/administration/logout/"]').click()
}
