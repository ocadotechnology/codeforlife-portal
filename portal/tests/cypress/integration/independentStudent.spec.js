/// <reference types="cypress" />

import { testMultipleLoginSessions } from "../support/multipleLoginSessionsTester.ts";
import { testRegistration } from "../support/registrationTester.ts";

describe("Independent student", () => {
  it("cannot login from multiple sessions", () => {
    testMultipleLoginSessions(cy.loginAsIndependentStudent, "/play/");
  });

  it("cannot register with invalid data", () => {
    const PASSWORD_TOO_WEAK_MESSAGE = `Password not strong enough, consider using at least 8 characters, upper and lower case letters, and numbers and making it hard to guess.`
    const PASSWORD_DO_NOT_MATCH_MESSAGE = `Your passwords do not match`
    const INVALID_NAME_MESSAGE = `Names may only contain letters, numbers, dashes, underscores, and spaces.`
    const INVALID_USERNAME_MESSAGE = `Usernames may only contain letters, numbers, dashes, and underscores.`

    testRegistration(cy.signupAsIndependentStudent,["Test Name", "TestUsername", "test@email.com", "pass", "pass"],
        false, PASSWORD_TOO_WEAK_MESSAGE);

    testRegistration(cy.signupAsIndependentStudent,["Test Name", "TestUsername", "test@email.com", "Password1!", "Password2!"],
        false, PASSWORD_DO_NOT_MATCH_MESSAGE);

    testRegistration(cy.signupAsIndependentStudent,["///", "TestUsername", "test@email.com", "Password1!", "Password1!"],
        false, INVALID_NAME_MESSAGE);

    testRegistration(cy.signupAsIndependentStudent,["Test Name", "///", "test@email.com", "Password1!", "Password1!"],
        false, INVALID_USERNAME_MESSAGE);
  });
});
