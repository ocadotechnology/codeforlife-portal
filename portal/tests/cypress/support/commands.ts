// ***********************************************
// This example commands.js shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

const defaultTeacherUsername = "alberteinstein@codeforlife.com";
const defaultTeacherPassword = "Password1";
const studentUsername = "Leonardo";
const studentAccessCode = "AB123";
const studentPassword = "Password1";
const independentStudentUsername = "indianajones@codeforlife.com";
const independentStudentPassword = "Password1";

Cypress.Commands.add("loginAsSuperuser", (username, password) => {
  cy.visit("/login/teacher/");

  cy.log("go to Teacher Login page");
  cy.get("#id_auth-username").type(username);
  cy.get("#id_auth-password").type(password);
  cy.get(".button--login").click();
});

Cypress.Commands.add("logout", () => {
  cy.get("#logout_menu").click();
  cy.get("#logout_button").click();
});

Cypress.Commands.add("adminLogout", () => {
  cy.visit("/administration/logout/");
});

Cypress.Commands.add("changeAdminPassword", (oldPassword, newPassword) => {
  cy.get("#id_old_password").type(oldPassword);
  cy.get("#id_new_password1").type(newPassword);
  cy.get("#id_new_password2").type(newPassword);
  cy.get("[type=submit]").click();
});

Cypress.Commands.add("deleteUser", (username) => {
  cy.get('[href="/administration/auth/user/"]').contains("Users").click();
  cy.get("a").contains(username).click();
  cy.get(".deletelink").contains("Delete").click();
  cy.get("[type=submit]").contains("Yes, I’m sure").click();
});

Cypress.Commands.add("anonymiseUser", (username) => {
  cy.get('[href="/administration/auth/user/"]').contains("Users").click();
  cy.get("th.field-username")
    .contains(username)
    .parents("tr")
    .find("input.action-select")
    .click();
  cy.get('div.actions select[name="action"]').select("anonymise_user");
  cy.get("div.actions button[type=submit]").click();
});

Cypress.Commands.add("loginAsTeacher", (teacherUsername, teacherPassword) => {
  cy.request("/login/teacher/");
  cy.getCookie("csrftoken").then((csrfToken) => {
    cy.request({
      method: "POST",
      url: "/login/teacher/",
      failOnStatusCode: true,
      form: true,
      body: {
        "auth-username": teacherUsername,
        "auth-password": teacherPassword,
        csrfmiddlewaretoken: csrfToken.value,
        "teacher_login_view-current_step": "auth",
      },
    });
    cy.visit("/teach/dashboard/");
  });
});

Cypress.Commands.add("loginAsDefaultTeacher", () => {
  cy.loginAsTeacher(defaultTeacherUsername, defaultTeacherPassword);
});

Cypress.Commands.add("loginAsStudent", () => {
  cy.request(`/login/student/${studentAccessCode}/`);
  cy.getCookie("csrftoken").then((csrfToken) => {
    cy.request({
      method: "POST",
      url: `/login/student/${studentAccessCode}/`,
      failOnStatusCode: true,
      form: true,
      body: {
        username: studentUsername,
        password: studentPassword,
        csrfmiddlewaretoken: csrfToken.value,
      },
    });
    cy.visit("/");
  });
});

Cypress.Commands.add("loginAsIndependentStudent", () => {
  cy.request("/login/independent/");
  cy.getCookie("csrftoken").then((csrfToken) => {
    cy.request({
      method: "POST",
      url: "/login/independent/",
      failOnStatusCode: true,
      form: true,
      body: {
        username: independentStudentUsername,
        password: independentStudentPassword,
        csrfmiddlewaretoken: csrfToken.value,
      },
    });
    cy.visit("/");
  });
});

Cypress.Commands.add(
  "signupAsTeacher",
  (firstName, lastName, email, password, confirmPassword) => {
    cy.visit("/register_form/");
    cy.get("#id_teacher_signup-teacher_first_name").type(firstName);
    cy.get("#id_teacher_signup-teacher_last_name").type(lastName);
    cy.get("#id_teacher_signup-teacher_email").type(email);
    cy.get("#id_teacher_signup-consent_ticked").click();
    cy.get("#id_teacher_signup-teacher_password").type(password);
    cy.get("#id_teacher_signup-teacher_confirm_password").type(confirmPassword);

    cy.get('[name="teacher_signup"]').click();
  }
);

Cypress.Commands.add(
  "signupAsIndependentStudent",
  (name, email, password, confirmPassword) => {
    cy.visit("/register_form/");
    cy.get("#id_independent_student_signup-name").type(name);
    cy.get("#id_independent_student_signup-email").type(email);
    cy.get("#id_independent_student_signup-is_over_required_age").check();
    cy.get("#id_independent_student_signup-password").type(password);
    cy.get("#id_independent_student_signup-confirm_password").type(
      confirmPassword
    );

    cy.get('[name="independent_student_signup"]').click();
  }
);
