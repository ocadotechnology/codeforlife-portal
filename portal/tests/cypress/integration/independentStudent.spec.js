/// <reference types="cypress" />

import { testMultipleLoginSessions } from '../support/multipleLoginSessionsTester.ts';
import { testRegistration } from '../support/registrationTester.ts';

describe('Independent student', () => {
  it('cannot login from multiple sessions', () => {
    testMultipleLoginSessions(cy.loginAsIndependentStudent, '/play/');
  });

  it('cannot register with invalid data', () => {
    const PASSWORD_TOO_WEAK_MESSAGE = `Password not strong enough, consider using at least 8 characters, upper and lower case letters, and numbers and making it hard to guess.`;
    const PASSWORD_DO_NOT_MATCH_MESSAGE = `Your passwords do not match`;
    const PASSWORD_TOO_COMMON_MESSAGE = `Password is too common, consider using a different password.`;
    const INVALID_NAME_MESSAGE = `Names may only contain letters, numbers, dashes, underscores, and spaces.`;

    testRegistration(
      cy.signupAsIndependentStudent,
      ['Test Name', 'test@email.com', 'pass', 'pass'],
      false,
      PASSWORD_TOO_WEAK_MESSAGE
    );

    testRegistration(
      cy.signupAsIndependentStudent,
      ['Test Name', 'test@email.com', '£EDCVFR$5tgb', '%TGBNHY^7ujm'],
      false,
      PASSWORD_DO_NOT_MATCH_MESSAGE
    );
    testRegistration(
      cy.signupAsIndependentStudent,
      ['Test Name','test@email.com', 'Password123$', 'Password123$'],
      false,
      PASSWORD_TOO_COMMON_MESSAGE
    );
    testRegistration(
      cy.signupAsIndependentStudent,
      ['///', 'test@email.com', '£EDCVFR$5tgb', '£EDCVFR$5tgb'],
      false,
      INVALID_NAME_MESSAGE
    );
  });
});
