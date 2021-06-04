/// <reference types="cypress" />

import { testMultipleLoginSessions } from "../support/multipleLoginSessionsTester.ts";

describe("Independent student", () => {
  it("cannot login from multiple sessions", () => {
    testMultipleLoginSessions(cy.loginAsIndependentStudent, "/play/");
  });
});
