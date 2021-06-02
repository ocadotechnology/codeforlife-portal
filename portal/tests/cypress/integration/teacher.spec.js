/// <reference types="cypress" />

import { testMultipleLoginSessions } from "../support/multipleLoginSessionsTester.ts";

describe("Teacher", () => {
  it("cannot login from multiple sessions", () => {
    testMultipleLoginSessions(cy.loginAsTeacher, "/teach/dashboard/");
  });
});
