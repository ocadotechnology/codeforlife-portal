/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    /**
     * Custom command to login as a superuser (admin) by navigating to the teacher login form.
     * @example cy.login("test_admin", "test_password")
     */
    loginAsSuperuser(username, password): Chainable<Element>

    /**
     * Custom command to change one's own password via the admin site.
     * @example cy.changeAdminPassword("password1", "password2")
     */
    changeAdminPassword(oldPassword, newPassword): Chainable<Element>

    /**
     * Custom command to delete a user via the admin site. Cypress finds the user by username, and clicks
     * the delete button.
     * @example cy.deleteUser("test_user")
     */
    deleteUser(username): Chainable<Element>
  }
}
