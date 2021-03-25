# Testing

Code for Life’s Portal runs tests using [pytest](https://docs.pytest.org/en/latest/).
The tests are found inside the `portal/tests` directory.

## Selenium tests

The selenium tests are run automatically when running `pytest`.
For them to run locally, you need to have chromedriver executable in your `PATH`.

You can find the list of chromedriver executables [here](https://chromedriver.storage.googleapis.com/index.html).

## Cypress tests

We are currently in the process of migrating from Selenium to Cypress. For more information
on our reasoning behind this, please ask someone from the team or read our Technical
Strategy document.

To run the Cypress tests, you need to run the following:

`yarn install`

`npx cypress run`

This will run the Cypress tests in the terminal.

If you want to view the tests as they run using Cypress' test runner window, you can run
`npx cypress open`.

## Snapshot tests

Running `pytest` will also automatically run the snapshot tests.
When needed, the snapshot tests can be updated by running `pytest --snapshot-update`.
