/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable {
    /**
     * Custom command to login as a superuser (admin) by navigating to the teacher login form.
     * @example cy.login("test_admin", "test_password")
     */
    loginAsSuperuser(username, password): Chainable<Element>;

    /**
     * Custom command to logout.
     * @example cy.logout()
     */
    logout(): Chainable<Element>;

    /**
     * Custom command to logout from admin panel.
     * @example cy.adminLogout()
     */
    adminLogout(): Chainable<Element>;

    /**
     * Custom command to change one's own password via the admin site.
     * @example cy.changeAdminPassword("password1", "password2")
     */
    changeAdminPassword(oldPassword, newPassword): Chainable<Element>;

    /**
     * Custom command to delete a user via the admin site. Cypress finds the user by username, and clicks
     * the delete button.
     * @example cy.deleteUser("test_user")
     */
    deleteUser(username): Chainable<Element>;

    /**
     * Custom command to anonymise a user via the admin site. Cypress finds the user by username, selects it and runs
     * the anonymise action.
     * @example cy.anonymiseUser("test_user")
     */
    anonymiseUser(username): Chainable<Element>;

    /**
     * Custom command to login with a teacher account that's created on the test server.
     * @example cy.loginAsTeacher("test@codeforlife.com", "testPassword")
     */
    loginAsTeacher(teacherUsername, teacherPassword): Chainable<Element>;

    /**
     * Custom command to login with the default teacher account that's created on the test server.
     * @example cy.loginAsTeacher()
     */
    loginAsDefaultTeacher(): Chainable<Element>;

    /**
     * Custom command to login with the default student account that's created on the test server.
     * @example cy.loginAsStudent()
     */
    loginAsStudent(): Chainable<Element>;

    /**
     * Custom command to login with the default independent student account that's created on the test server.
     * @example cy.loginAsIndependentStudent()
     */
    loginAsIndependentStudent(): Chainable<Element>;

    /**
     * Custom command to signup as teacher.
     * @example cy.signupAsTeacher("Test Name", "Test Last Name", "test@email.com", "testPassword", "testPassword")
     */
    signupAsTeacher(
      firstName,
      lastName,
      email,
      password,
      confirmPassword
    ): Chainable<Element>;

    /**
     * Custom command to signup as an independent student.
     * @example cy.signupAsIndependentStudent("Test Name", "test@email.com", "testPassword", "testPassword")
     */
    signupAsIndependentStudent(
      name,
      email,
      password,
      confirmPassword
    ): Chainable<Element>;
  }
}
