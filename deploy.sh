#!/bin/bash
pip install https://www.djangoproject.com/download/1.7c1/tarball/
pip install https://bitbucket.org/rptlab/reportlab/get/tip.zip
ssh-agent /opt/codeforlife-deploy/install-portal.sh
ssh-agent /opt/codeforlife-deploy/install-rapid-router.sh
ls -d /usr/local/lib/python2.7/dist-packages/* | grep -v info | grep -v PIL | xargs -i cp -R {} /opt/codeforlife-deploy/
# To be used to docker deployment environment
cd /opt/codeforlife-deploy/
export DEPLOYMENT=1
./manage.py collectstatic --noinput
./manage.py migrate
# flush memcache
echo "from django.core.cache import cache; cache.clear()" | ./manage.py shell
appcfg.py update --authenticate_service_account $DEPLOYMENT_CONFIG
