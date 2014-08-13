#!/bin/bash

# This script installs ocargo and the portal, sets up virtualenv, and
# sets some aliases in ~/.bashrc for ease of use.
# It requires that python-dev, pip and gem are installed.

DEPLOY_PATH=`pwd`

# install virtualenv
sudo pip install virtualenv

# create virtual env
rm -rf VIRTUALENV
virtualenv VIRTUALENV
source VIRTUALENV/bin/activate

# clone the other repositories
echo "Cloning other git repositories"
cd ..
PROJECT_PATH=`pwd`

if [ ! -d ocargo ]; then
    git clone https://github.com/ocadotechnology/ocargo ocargo
fi

if [ ! -d portal ]; then
    git clone https://github.com/ocadotechnology/codeforlife-portal portal
fi

# install requirements
cd ${DEPLOY_PATH}
./install-requirements.sh

# now change to symlinks,
# this means that local changes affect the running server immediately
# without the need to install requirements again or restart the server
rm -rf VIRTUALENV/lib/python2.7/site-packages/{game,portal}
ln -sv ${PROJECT_PATH}/ocargo/game VIRTUALENV/lib/python2.7/site-packages/game
ln -sv ${PROJECT_PATH}/ocargo/nuit VIRTUALENV/lib/python2.7/site-packages/nuit
ln -sv ${PROJECT_PATH}/ocargo/reports VIRTUALENV/lib/python2.7/site-packages/reports
ln -sv ${PROJECT_PATH}/ocargo/website VIRTUALENV/lib/python2.7/site-packages/website
ln -sv ${PROJECT_PATH}/portal/portal VIRTUALENV/lib/python2.7/site-packages/portal

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