/// <reference types="cypress" />

import { testMultipleLoginSessions } from "../support/multipleLoginSessionsTester.ts";
import { testRegistration } from "../support/registrationTester.ts";

describe("Teacher", () => {
  it("cannot login from multiple sessions", () => {
    testMultipleLoginSessions(cy.loginAsTeacher, "/teach/dashboard/");
  });

  it("cannot register with invalid data", () => {
    const PASSWORD_TOO_WEAK_MESSAGE = `Password not strong enough, consider using at least 10 characters, upper and lower case letters, numbers, special characters and making it hard to guess.`
    const PASSWORD_DO_NOT_MATCH_MESSAGE = `The password and the confirmation password do not match`

    testRegistration(cy.signupAsTeacher,["Test Name", "Test Last Name", "test@email.com", "pass", "pass"],
        false, PASSWORD_TOO_WEAK_MESSAGE);

    testRegistration(cy.signupAsTeacher,["Test Name", "Test Last Name", "test@email.com", "StrongPassword1!", "StrongPassword2!"],
        false, PASSWORD_DO_NOT_MATCH_MESSAGE);
  });
});
