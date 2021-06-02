/// <reference types="cypress" />

import { testMultipleLoginSessions } from "../support/multipleLoginSessionsTester.ts";

describe("Student", () => {
  it("cannot login from multiple sessions", () => {
    testMultipleLoginSessions(cy.loginAsStudent, "/play/");
  });
});
