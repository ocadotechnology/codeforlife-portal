/// <reference types="cypress" />

import {
  createClass,
  createStudent,
  deleteAllStudents,
  deleteClass,
  editClassSettings,
  goToClassSettings,
  transferClass,
} from "../support/classTester.ts";
import { testMultipleLoginSessions } from "../support/multipleLoginSessionsTester.ts";
import { testRegistration } from "../support/registrationTester.ts";

describe("Teacher", () => {
  it("cannot login from multiple sessions", () => {
    testMultipleLoginSessions(cy.loginAsDefaultTeacher, "/teach/dashboard/");
  });

  it("cannot register with invalid data", () => {
    const PASSWORD_TOO_WEAK_MESSAGE = `Password not strong enough, consider using at least 10 characters, upper and lower case letters, numbers, special characters and making it hard to guess.`;
    const PASSWORD_DO_NOT_MATCH_MESSAGE = `The password and the confirmation password do not match`;
    const PASSWORD_TOO_COMMON_MESSAGE = `Password is too common, consider using a different password.`;

    testRegistration(
      cy.signupAsTeacher,
      ["Test Name", "Test Last Name", "test@email.com", "pass", "pass"],
      false,
      PASSWORD_TOO_WEAK_MESSAGE
    );

    testRegistration(
      cy.signupAsTeacher,
      [
        "Test Name",
        "Test Last Name",
        "test@email.com",
        "Password123$",
        "Password123$",
      ],
      false,
      PASSWORD_TOO_COMMON_MESSAGE
    );

    testRegistration(
      cy.signupAsTeacher,
      [
        "Test Name",
        "Test Last Name",
        "test@email.com",
        "czYuH)g0FbD_5E9/",
        "czYuH)g0FbD_5E9//",
      ],
      false,
      PASSWORD_DO_NOT_MATCH_MESSAGE
    );
  });

  it("can delete a class only when empty", () => {
    // Login as Portaladmin
    cy.loginAsSuperuser("codeforlife-portal@ocado.com", "abc123");

    cy.get("#tab-classes").click();

    createClass();
    createStudent();
    cy.get("#back_to_class_button").click();

    // Try to delete class
    deleteClass();

    cy.get("#messages").should("be.visible");
    cy.get("#messages").should(
      "contain.text",
      `This class still has students, please remove or delete them all before deleting the class.`
    );

    // Delete all students and try again
    deleteAllStudents();
    deleteClass();

    // Check class no longer exists
    cy.get("#classes-table").should("not.contain.text", `Test Class`);

    cy.logout();
  });

  it("can edit a class", () => {
    // Login as Portaladmin
    cy.loginAsSuperuser("codeforlife-portal@ocado.com", "abc123");

    cy.get("#tab-classes").click();

    createClass();
    goToClassSettings();

    // Check class settings
    cy.get("#id_name").invoke("val").should("equal", "Test Class");
    cy.get("#id_classmate_progress").should("not.be.checked");
    cy.get(".container").should(
      "contain.text",
      `This class is not currently accepting external requests.`
    );

    editClassSettings("New Test Class", true, "1000");
    goToClassSettings();

    // Check new class settings
    cy.get("#id_name").invoke("val").should("equal", "New Test Class");
    cy.get("#id_classmate_progress").should("be.checked");
    cy.get(".container").should(
      "contain.text",
      `This class is currently set to always accept requests.`
    );

    cy.get("#return_to_class_button").click();

    // Cleanup
    deleteClass();

    // Check class no longer exists
    cy.get("#classes-table").should("not.contain.text", `Test Class`);

    cy.logout();
  });

  it("can transfer a class", () => {
    // Login as Portaladmin
    cy.loginAsSuperuser("codeforlife-portal@ocado.com", "abc123");

    cy.get("#tab-classes").click();

    createClass();
    createStudent();
    cy.get("#back_to_class_button").click();
    goToClassSettings();

    // Transfer class to Max Planck
    transferClass("2");
    cy.logout();

    // Login as Max Planck
    cy.loginAsSuperuser("maxplanck@codeforlife.com", "Password1");

    // Check class and student exist
    cy.get("#tab-classes").click();
    cy.get("#classes-table").should("contain.text", `Test Class`);
    cy.get('[href^="/teach/class/"]').last().click();
    cy.get("#student_table").should("contain.text", `Test Student`);

    // Cleanup
    deleteAllStudents();
    deleteClass();

    // Check class no longer exists
    cy.get("#classes-table").should("not.contain.text", `Test Class`);

    cy.logout();
  });

  it('cannot see an anonymised teacher in dashboard', () => {
    const teacherEmail = 'teacher.to.be.deleted2@codeforlife.com'; // from teachersToBeDeleted fixture
    const teacherName = 'Teacher To Be Deleted 2';

    // Login as default teacher and check the teacher is in the teachers table
    cy.loginAsDefaultTeacher();
    cy.get('#teachers_table').should('contain.text', teacherName);
    cy.logout();

    // Login as Portaladmin, go to admin site and anonymise teacher
    cy.loginAsSuperuser('codeforlife-portal@ocado.com', 'abc123');
    cy.visit('administration/');
    cy.anonymiseUser(teacherEmail);
    cy.visit("/")
    cy.logout();

    // Login as default teacher again and check the teacher is not there now
    cy.loginAsDefaultTeacher();
    cy.get('#teachers_table').should('not.contain', teacherName);
    cy.get('#teachers_table').should('not.contain', 'Deleted User');
  });
});
