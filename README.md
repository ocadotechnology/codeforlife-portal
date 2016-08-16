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
* Clone the repo
* Make and activate a virtualenv (We recommend [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/index.html))
    * e.g. the first time, `mkvirtualenv -a path/to/codeforlife-portal codeforlife-portal`
    * and thereafter `workon codeforlife-portal`
* `./run` - This will:
    * install all of the dependencies using pip
    * sync the database
    * collect the static files
    * run the server

## Common Problems
### Unapplied migrations on first run
It may be that some migrations were changed and you have .pyc files from the old ones. Try removing all .pyc migrations by running `rm migrations/*.pyc` from the ocargo repository.
