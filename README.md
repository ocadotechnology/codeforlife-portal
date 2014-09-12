# cfl-deploy

A django package to wrap up and deploy all Code for Life apps and backend. This package has all of the other apps (currently portal and ocargo) as requirements and allows them to depend on each other.

To run any of the subprojects it is currently necessary to download all of them and run the server from this deploy app. To make this as easy as possible (on unix like systems at least) there is a script in this project called local-setup.sh which handles installing all the dependencies and setting up the other respositories for development work. This script will clone the ocargo and portal repositories if they are not already present into the same directory as where you cloned the deploy repository, create a virtual environment for all the python packages, install all dependencies and set up symbolic links from the virtual env to the other repositories. These symbolic links, while perhaps unusual, allow you to make changes to the other repositories without having to reinstall them with pip after each change.

**So, to reiterate, to get all of the site running locally, simply clone this repository and run ./local-setup.sh**

## FAQ:
- ###### Where do I commit from
You should commit code from the repository it comes from in the normal way. They are completely separate repositories and you will need to commit / pull / push each one separately.

- ###### How many virtualenvs should I have
You should only have one and it should be in the deploy directory. You should have this activated at all times, which you can do by running "source VIRTUALENV/bin/activate" in the deploy directory or "source ../codeforlife-deploy/VIRTUALENV/bin/activate" from one of the other repos.

- ###### How do I run the server
We use the default django operations or migrate, collectstatic and runserver. To run any of these you will need to have your virtualenv activated which is explained above.

The structure of all of the commands is python [path/to/]manage.py [command]. If you're running form the deploy repo (as you should be) the you can just use manage.py but from another repo you can use ../codeforlife-deploy/manage.py

The basic operations are
  - to migrate / sync / create the database      - python manage.py migrate
  - to collect static files                      - python manage.py collectstatic [--noinput]
  - to run the server                            - python manage.py runserver [0.0.0.0:8000]
  - (There is a nice alias for these called rs which performs all of the above which local-setup.sh should add to your ~/.bashrc file, mac users can add this to ~/.profile manually if they wish to use it.)

- ###### Making migrations, ie: changes to the models
Running makemigrations is slightly more complicated, but not much! The workflow is: you make your changes to the models, you run python manage.py makemigrations, you run python manage.py migrate.

If you are using the local-setup.sh script and hence have symlinks setup in your virtualenv then you can run makemigrations from the deploy directory and it will all work. If you are not using symlinks (windows users?) then you should run it from the repo where you made the changes using python ../codeforlife-deploy/manage.py makemigrations. The danger is that migrations may be created within the virtualenv and be lost.

- ###### Connect to local server from IPad using a Wifi hotspot
Start the server using 'python manage.py runserver 0.0.0.0:8000' to allow connections from places other than localhost. Use ifconfig to find the ip address of your hotspot.

## Common problems:
- ###### Errors about clashing models, particularly userprofile, etc...
You probably have an old copy of ocargo, please pull the latest changes and try migrating and running the server again.

- ###### Errors about django not being installed
It's possible you're running the system copy of python rather than virtualenv's copy, try using VIRTUALENV/bin/python and see if that fixes the problem.

- ###### Unapplied migrations on first run
Some migrations were changed and you may have .pyc files left over of the old versions which confuses things, try clearing them all out of ocargo by running rm game/migrations/*.pyc from the ocargo repository.
