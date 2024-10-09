/// <reference types="cypress" />

describe('User', () => {
  it('can open donate popup', () => {
    cy.get('#donate').click();
    cy.get('.popup-box').should('be.visible');
    cy.get('#donate_form').should('be.visible');
  });
});
