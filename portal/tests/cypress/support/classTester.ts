/// <reference types="cypress" />

export function createClass() {
  cy.get('#id_class_name').type("Test Class");
  cy.get('#create_class_button').click();

  cy.get('#messages').should('be.visible');
  cy.get('#messages').should('contain.text', `The class 'Test Class' has been created successfully.`);
}

export function createStudent() {
  cy.get('#id_names').type("Test Student");
  cy.get('#submitStudents').click();

  cy.get('#onboarding_student_list_page').should('exist');
}

export function deleteClass() {
  cy.get('#deleteClass').click();
  cy.get('#popup').should('be.visible');
  cy.get('#confirm_button').click();
}

export function deleteAllStudents() {
  cy.get('#selectedStudentsListToggle').check();
  cy.get('#deleteSelectedStudents').click();
  cy.get('#popup').should('be.visible');
  cy.get('#confirm_button').click();

  cy.get('.student-table__cell').should('not.exist');
}

export function goToClassSettings() {
  cy.get('#class_settings_button').click();
  cy.get('#teach_edit_class_page').should('exist');
}

export function editClassSettings(className, isProgressShared, externalRequestsValue) {
  cy.get('#id_name').clear().type(className);

  if(isProgressShared) {
    cy.get('#id_classmate_progress').check();
  }
  else {
    cy.get('#id_classmate_progress').uncheck();
  }

  cy.get('#id_external_requests').select(externalRequestsValue);
  cy.get('#update_button').click();

  cy.get('#messages').should('be.visible');
  cy.get('#messages').should('contain.text', `The class's settings have been changed successfully.`);
}

export function transferClass(newTeacherID) {
  cy.get('#id_new_teacher').select(newTeacherID);
  cy.get('#move_button').click();

  cy.get('#messages').should('be.visible');
  cy.get('#messages').should('contain.text', `The class has been successfully assigned to a different teacher.`);
}
