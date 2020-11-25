![Build Status](https://github.com/ocadotechnology/codeforlife-portal/workflows/CI%2FCD/badge.svg)
[![codecov](https://codecov.io/gh/ocadotechnology/codeforlife-portal/branch/master/graph/badge.svg)](https://codecov.io/gh/ocadotechnology/codeforlife-portal)
[![Code Climate](https://codeclimate.com/github/ocadotechnology/codeforlife-portal/badges/gpa.svg)](https://codeclimate.com/github/ocadotechnology/codeforlife-portal)

## A [Code for Life](https://www.codeforlife.education/) repository

- Ocado Technology's [Code for Life initiative](https://www.codeforlife.education/) has been developed to inspire the next generation of computer scientists and to help teachers deliver the computing curriculum.
- This repository hosts the source code of the **main website**: the portal for the Code For Life initiative, the registration/log in, the teachers' dashboards, the teaching materials, etc
- The other repos for Code For Life:
  - the first game, [Rapid Router](https://github.com/ocadotechnology/rapid-router)
  - the new game for teenagers, [currently at a very early stage](https://github.com/ocadotechnology/aimmo)
  - the [deployment code for Google App Engine](https://github.com/ocadotechnology/codeforlife-deploy-appengine)

## Running Locally

- Clone the repo. Fork it first if you want to contribute, or make sure you work on separate branches.
- Install prerequisites. E.g. on Ubuntu / Linux Mint:
  - `sudo apt-get install git`
  - `sudo apt-get install python-dev`
  - `sudo apt-get install libxml2-dev libxslt1-dev zlib1g-dev`
- Make and activate a virtualenv (We recommend [pipenv](<(https://docs.pipenv.org/)>))
  - On **Mac**, run `brew install pipenv` using the `brew` package manager. Then run `pipenv install` followed by `pipenv shell`.
  - On Linux, follow the instructions [here](https://docs.pipenv.org/install/#installing-pipenv) to install pipenv. Then run `pipenv install` followed by `pipenv shell`.
- `./run` - This will:
  - sync the database
  - collect the static files
  - run the server
- Once you see `Quit the server with CONTROL-C`, you can open the portal in your browser at `localhost:8000`.

- To setup test dependencies run `pipenv install --dev` and then `pytest` to run tests.

- If you have problems seeing the portal on machines with different locale (e.g. Polish), check the terminal for errors mentioning `ValueError: unknown locale: UTF-8`. If you see them, you need to have environment variables `LANG` and `LC_ALL` both set to `en_US.UTF-8`.
  - Either export them in your `.bashrc` or `.bash_profile`
  - or restart the portal with command `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./run`.

## How to contribute!

**Guidelines** Read the [contributing guidelines](CONTRIBUTING.md), thanks!<br>
You can also read about the [life cycle of a code change](docs/life-cycle-of-a-code-change.md).

One word of caution: please do not add any issues related to security. Evil hackers are everywhere nowadays... If you do find a security issue, let us know using our [contact form][c4l-contact-form].

**Want to help?** You can contact us using this [contact form][c4l-contact-form] and we'll get in touch as soon as possible! Thanks a lot.

## Common Problems

### Unapplied migrations on first run

It may be that some migrations were changed and you have .pyc files from the old ones. Try removing all .pyc migrations by running `rm migrations/*.pyc` from the repository.

### Mac OS Mojave

On MacOS Mojave there is an error when installing `Pillow 3.3.2`.
To fix this issue you need to run the following command:

```
sudo installer -pkg /Library/Developer/CommandLineTools/Packages/macOS_SDK_headers_for_macOS_10.14.pkg -target /
```

cf: https://github.com/python-pillow/Pillow/issues/3438#issuecomment-435169249

[c4l-contact-form]: https://www.codeforlife.education/help/#contact
