# cfl-deploy

A django package to wrap up and deploy all Code for Life apps and backend. This package has all of the other apps (currently portal and ocargo) as requirements and allows some of them to depend on each other.

To run any of the subprojects it is currently necessary to download all of them and run the server from this deploy app. To make this as easy as possible (on unix like systems at least) there is a script in this project called local-setup.sh which handles installing all the dependencies and setting up the other respositories for development work. This script will clone the ocargo and portal repositories if they are not already present into the same directory as where you cloned the deploy repository, create a virtual environment for all the python packages, install all dependencies and set up symbolic links from the virtual env to the other repositories. These symbolic links, while perhaps unusual, allow you to make changes to the other repositories without having to reinstall them with pip after each change.

**So, to reiterate, to get all of the site running locally, simply clone this repository and run ./local-setup.sh**

## FAQ:
- ###### Where do I commit from
You should commit code from the repository it comes from in the normal way.

- ###### How do I run the server
You run all manage.py commands from the deploy directory (apart from makemigrations, explained next),
  - to migrate / sync the database - python manage.py migrate
  - to collect static - python manage.py collectstatic [--noinput]
  - to run the server - python manage.py runserver
  - (There is a nice alias for these called rs which performs all of the above which local-setup.sh should add to your ~/.bashrc file, mac users can add this to ~/.profile manually if they wish to use it.)

- ###### Making migrations
You should make migrations from the repository where you've changed the models, this will make sure that the migration file is created in the correct place in the correct repository. If you run makemigrations from the deploy directory the migration file may be created in the virtualenv and be lost.

## Common problems:
- ###### Errors about clashing models, particularly userprofile, etc...
You probably have an old copy of ocargo, please pull the latest changes and try migrating and running the server again.

- ###### Errors about django not being installed
It's possible you're running the system copy of python rather than virtualenv's copy, try using VIRTUALENV/bin/python and see if that fixes the problem.

- ###### Unapplied migrations on first run
Some migrations were changed and you may have .pyc files left over of the old versions which confuses things, try clearing them all out of ocargo by running rm game/migrations/*.pyc from the ocargo repository.
