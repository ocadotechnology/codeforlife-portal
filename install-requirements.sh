#!/bin/bash
# find out where we are
DEPLOY_PATH=`pwd`
cd ..
PROJECT_PATH=`pwd`
cd ${DEPLOY_PATH}

# create virtual env
rm -rf VIRTUALENV
virtualenv VIRTUALENV
source VIRTUALENV/bin/activate

pip install -r requirements.txt
pip install https://www.reportlab.com/pypi/packages/reportlab-3.1.47.tar.gz

pip install -r ../ocargo/requirements.txt
pip install -r ../portal/requirements.txt

# Point the pre-push hook to the pre-push in ocargo.
echo 'Setting up the pre-push hooks.'
# ocargo 
echo '#!/bin/bash' > ../ocargo/.git/hooks/pre-push
echo 'bash pre-push' >> ../ocargo/.git/hooks/pre-push
chmod +x ../ocargo/.git/hooks/pre-push
chmod +x ../ocargo/pre-push
# portal
echo '#!/bin/bash' > ../portal/.git/hooks/pre-push
echo 'bash pre-push' >> ../portal/.git/hooks/pre-push
chmod +x ../portal/.git/hooks/pre-push
chmod +x ../portal/pre-push
# deploy
echo '#!/bin/bash' > .git/hooks/pre-push
echo 'bash pre-push' >> .git/hooks/pre-push
chmod +x .git/hooks/pre-push
chmod +x pre-push

# now change to symlinks,
# this means that local changes affect the running server immediately
# without the need to install requirements again or restart the server
rm -rf VIRTUALENV/lib/python2.7/site-packages/{game,portal}
ln -sv ${PROJECT_PATH}/ocargo/game VIRTUALENV/lib/python2.7/site-packages/game
ln -sv ${PROJECT_PATH}/portal/portal VIRTUALENV/lib/python2.7/site-packages/portal
ln -sv ${PROJECT_PATH}/portal/reports VIRTUALENV/lib/python2.7/site-packages/reports
ln -sv ${PROJECT_PATH}/portal/ratelimit VIRTUALENV/lib/python2.7/site-packages/ratelimit
