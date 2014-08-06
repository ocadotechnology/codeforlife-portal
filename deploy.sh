#!/bin/bash
echo $SSH_KEY > /root/.ssh/id_rsa
pip install -r /opt/codeforlife-deploy/requirements.txt
ls -d /usr/local/lib/python2.7/dist-packages/* | grep -v info | xargs -i cp -R {} /opt/codeforlife-deploy/
# To be used to docker deployment environment
export DEPLOYMENT=1
./manage.py collectstatic --noinput
./manage.py migrate
# flush memcache
echo "from django.core.cache import cache; cache.clear()" | ./manage.py shell
appcfg.py update --authenticate_service_account $DEPLOYMENT_CONFIG
