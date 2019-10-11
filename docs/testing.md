# Testing

Code for Life’s Portal runs tests using [pytest](https://docs.pytest.org/en/latest/).
The tests are found inside the `portal/tests` directory.

## Selenium tests

The selenium tests are run automatically when running `pytest`.
For them to run locally, you need to have chromedriver executable in your `PATH`.

You can find the list of chromedriver executables [here](https://chromedriver.storage.googleapis.com/index.html).

## Snapshot tests

Running `pytest` will also automatically run the snapshot tests.
When needed, the snapshot tests can be updated by running `pytest --snapshot-update`.
