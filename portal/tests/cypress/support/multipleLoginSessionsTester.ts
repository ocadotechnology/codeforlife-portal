/// <reference types="cypress" />

export function testMultipleLoginSessions(loginFunction, loggedInUserUrl) {
  // log in, check the user is logged in and get the session cookie.
  loginFunction();
  cy.get("#logout_menu").should("exist");
  cy.getCookie("sessionid")
    .should("exist")
    .then((c) => {
      let initialSessionId = c.value;

      // clear cookies, then set the cookie again and make sure user is still logged in
      cy.clearCookies();
      cy.setCookie("sessionid", initialSessionId);
      cy.visit(loggedInUserUrl);
      cy.get("#logout_menu").should("exist");

      // clear cookies and check if the user is logged out
      cy.clearCookies();
      cy.visit(loggedInUserUrl);
      cy.get("#logout_menu").should("not.exist");

      // log in on a new session and check the user is logged in
      loginFunction();
      cy.get("#logout_menu").should("exist");

      // clear cookies, set the initial session cookie, visit a logged in page and the user should be logged out
      cy.clearCookies();
      cy.setCookie("sessionid", initialSessionId);
      cy.visit(loggedInUserUrl);
      cy.get("#logout_menu").should("not.exist");
    });
}
