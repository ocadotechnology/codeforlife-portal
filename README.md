# [Code for Life](https://www.codeforlife.education/) Portal

[![Workflow Status](https://github.com/ocadotechnology/codeforlife-portal/actions/workflows/ci.yml/badge.svg)](https://github.com/ocadotechnology/codeforlife-portal/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/ocadotechnology/codeforlife-portal/branch/master/graph/badge.svg)](https://codecov.io/gh/ocadotechnology/codeforlife-portal)

Ocado Technology's [Code for Life initiative](https://www.codeforlife.education/) has been developed to inspire the next generation of computer scientists and to help teachers deliver the computing curriculum.

This repository hosts the source code of the **main website**: the portal for the Code For Life initiative, the registration/log in, the teachers' dashboards, the teaching materials, etc.

The other repos for Code For Life:

- our first game, [Rapid Router](https://github.com/ocadotechnology/rapid-router)
- our second game for older children: [Kurono (code name: aimmo)](https://github.com/ocadotechnology/aimmo)
- the [deployment code for Google App Engine](https://github.com/ocadotechnology/codeforlife-deploy-appengine)

## How to set up and run locally

### Ubuntu / Linux Mint

- Run `sudo apt-get install python-dev`.

- Run `sudo apt-get update` to save having to do it later in the process.

- Follow the instructions for [installing pyenv](https://github.com/pyenv/pyenv#installation).

- Run `sudo apt-get install python-pip`.

- Run `pip install pipenv` to get the [pipenv](https://pipenv.readthedocs.io/en/latest/) virtual environment.

### Mac

- Get the [brew](https://brew.sh/) package manager.

- It's recommended to update sqlite3 as Mac default version may be incompatible. Check [common issues here](https://github.com/ocadotechnology/aimmo/blob/development/docs/common-issues.md).  
  To update sqlite3 with brew: `brew install sqlite3`. Then follow the instructions in `brew info sqlite3` before installing a python version with `pyenv`.

```
If you need to have sqlite first in your PATH, run:
  echo 'export PATH="/usr/local/opt/sqlite/bin:$PATH"' >> ~/.zshrc

For compilers to find sqlite you may need to set:
  export LDFLAGS="-L/usr/local/opt/sqlite/lib"
  export CPPFLAGS="-I/usr/local/opt/sqlite/include"
```

- Then install pyenv with the right sqlite3 version (make sure `LDFLAGS` and `CPPFLAGS` are set as above): `brew install pyenv`.

- Run `brew install pipenv`.

### Development and tests

- Run `pipenv install --dev` to get the requirements for the project.

- Followed by `pipenv shell` to activate the virtual env.

- `./run` - This will:
  - sync the database
  - collect the static files
  - run the server
- Once you see `Quit the server with CONTROL-C`, you can open the portal in your browser at `localhost:8000`.

- Run `pytest` to run unit tests. All tests will be run on github when PR is submitted, but it's good to check locally too to make sure the tests run successfully after your changes.

### Localisation

- If you have problems seeing the portal on machines with different locale (e.g. Polish), check the terminal for errors mentioning `ValueError: unknown locale: UTF-8`. If you see them, you need to have environment variables `LANG` and `LC_ALL` both set to `en_US.UTF-8`.
  - Either export them in your `.bashrc` or `.bash_profile`
  - or restart the portal with command `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./run`.

## How to contribute

Please read the [contributing guidelines](CONTRIBUTING.md).
