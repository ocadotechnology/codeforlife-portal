[![Build Status](https://travis-ci.org/ocadotechnology/codeforlife-portal.svg?branch=master)](https://travis-ci.org/ocadotechnology/codeforlife-portal)
[![Coverage Status](https://coveralls.io/repos/ocadotechnology/codeforlife-portal/badge.svg?branch=master&service=github)](https://coveralls.io/github/ocadotechnology/codeforlife-portal?branch=master)
[![Code Climate](https://codeclimate.com/github/ocadotechnology/codeforlife-portal/badges/gpa.svg)](https://codeclimate.com/github/ocadotechnology/codeforlife-portal)

## A  [Code for Life](https://www.codeforlife.education/) repository
* Ocado Technology's [Code for Life initiative](https://www.codeforlife.education/) has been developed to inspire the next generation of computer scientists and to help teachers deliver the computing curriculum.
* This repository hosts the source code of the **main website**: the portal for the Code For Life initiative, the registration/log in, the teachers' dashboards, the teaching materials, etc
* The other repos for Code For Life:
    * the first game, [Rapid Router](https://github.com/ocadotechnology/rapid-router)
    * the new game for teenagers, [currently at a very early stage](https://github.com/ocadotechnology/aimmo)
    * the [deployment code for Google App Engine](https://github.com/ocadotechnology/codeforlife-deploy-appengine)

## Running Locally
* Clone the repo. Fork it first if you want to contribute, or make sure you work on separate branches.
* Install prerequisites. E.g. on Ubuntu / Linux Mint:
    * `sudo apt-get install git`
    * `sudo apt-get install python-dev`
    * `sudo apt-get install libxml2-dev libxslt1-dev zlib1g-dev`
* Make and activate a virtualenv (We recommend [pipenv]((https://docs.pipenv.org/)))
    * On **Mac**, run `brew install pipenv` using the `brew` package manager. Then run `pipenv install` followed by `pipenv shell`.
    * On Linux, follow the instructions [here](https://docs.pipenv.org/install/#installing-pipenv) to install pipenv. Then run `pipenv install` followed by `pipenv shell`. 
    * create settings file under `example_project/example_project/local_settings.py` with `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`
* `./run` - This will:
    * sync the database
    * collect the static files
    * run the server
* Once you see `Quit the server with CONTROL-C`, you can open the portal in your browser at `localhost:8000`.

* To setup test dependencies and run tests, you can use `python setup.py test`

* If you have problems seeing the portal on machines with different locale (e.g. Polish), check the terminal for errors mentioning `ValueError: unknown locale: UTF-8`. If you see them, you need to have environment variables `LANG` and `LC_ALL` both set to `en_US.UTF-8`.
    * Either export them in your `.bashrc` or `.bash_profile`
    * or restart the portal with command `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./run`.

## How to contribute!
__Guidelines__ Read the [contributing guidelines](CONTRIBUTING.md), thanks!<br>
One word of caution: please do not add any issues related to security. Evil hackers are everywhere nowadays... If you do find a security issue, let us know using our [contact form][c4l-contact-form].

__Want to help?__ You can contact us using this [contact form][c4l-contact-form] and we'll get in touch as soon as possible! Thanks a lot.

## Common Problems
### Unapplied migrations on first run
It may be that some migrations were changed and you have .pyc files from the old ones. Try removing all .pyc migrations by running `rm migrations/*.pyc` from the repository.

[c4l-contact-form]: https://www.codeforlife.education/help/#contact
