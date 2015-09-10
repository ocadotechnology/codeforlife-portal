#!/bin/bash

# This script installs ocargo and the portal, sets up virtualenv, and
# sets some aliases in ~/.bashrc for ease of use.
# It requires that python-dev, pip and gem are installed.

DEPLOY_PATH=`pwd`

# install virtualenv
sudo pip install virtualenv

# clone the other repositories
echo "Cloning other git repositories"
cd ..

if [ ! -d ocargo ]; then
    git clone https://github.com/ocadotechnology/ocargo ocargo
fi

# create virtualenv and install requirements
cd ${DEPLOY_PATH}
./scripts/install-requirements.sh

# install sass, (to be able to switch to and from prod requirements.txt)
sudo gem install sass --version "3.3.4"



# Adds aliases to ~/.bashrc, for ease of use
touch ~/.bashrc

echo "alias vac='source VIRTUALENV/bin/activate'" >> ~/.bashrc
echo "alias rs='vac && VIRTUALENV/bin/python manage.py migrate && VIRTUALENV/bin/python manage.py collectstatic --noinput && VIRTUALENV/bin/python manage.py runserver'" >> ~/.bashrc



echo "run 'source ~/.bashrc' to pick the new aliases"
echo "run 'vac' or 'source VIRTUALENV/bin/activate' to activate your virtualenv, and run 'deactivate' to deactivate it"
echo "then run 'rs' or './manage.py runserver' to run a local runserver"
echo "then you can navigate to http://localhost:8000"

# sync the db and collect static
source VIRTUALENV/bin/activate
VIRTUALENV/bin/python manage.py migrate
VIRTUALENV/bin/python manage.py collectstatic --noinput