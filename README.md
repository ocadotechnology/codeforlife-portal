[![Build Status](https://travis-ci.org/ocadotechnology/codeforlife-portal.svg?branch=master)](https://travis-ci.org/ocadotechnology/codeforlife-portal)
[![Coverage Status](https://coveralls.io/repos/ocadotechnology/codeforlife-portal/badge.svg?branch=master&service=github)](https://coveralls.io/github/ocadotechnology/codeforlife-portal?branch=master)
[![Code Climate](https://codeclimate.com/github/ocadotechnology/codeforlife-portal/badges/gpa.svg)](https://codeclimate.com/github/ocadotechnology/codeforlife-portal)

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
