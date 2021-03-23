/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    /**
     * Custom command to login with the default admin account that's created on the test server.
     * @example cy.login()
     */
    loginAsSuperuser(username, password): Chainable<Element>

    /**
     * Custom command to login with the default admin account that's created on the test server.
     * @example cy.login()
     */
    changeAdminPassword(oldPassword, newPassword): Chainable<Element>

    /**
     * Custom command to login with the default admin account that's created on the test server.
     * @example cy.login()
     */
    deleteUser(username): Chainable<Element>
  }
}
