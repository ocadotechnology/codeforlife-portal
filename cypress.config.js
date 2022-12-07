module.exports = {
  projectId: 'hcq23q',
  videoUploadOnPasses: false,
  e2e: {
    setupNodeEvents(on, config) {},
    baseUrl: 'http://localhost:8000',
    specPattern: 'portal/tests//**/*.spec.js',
    supportFile: 'portal/tests/cypress/support/index.js',
  },
}
