#!/bin/bash
./build.sh
# To be used to docker deployment environment
export DEPLOYMENT=1
./manage.py collectstatic --noinput
./manage.py compress -f
./manage.py migrate
MIGRATERESULT=$?
if [ $MIGRATERESULT -ne 0 ]; then
  echo "Migrations failed"
  exit 1
fi
# flush memcache
echo "from django.core.cache import cache; cache.clear()" | ./manage.py shell
appcfg.py update --authenticate_service_account \
  -E DJANGO_SECRET:$DJANGO_SECRET \
  -E RECAPTCHA_PRIVATE_KEY:$RECAPTCHA_PRIVATE_KEY \
  -E RECAPTCHA_PUBLIC_KEY:$RECAPTCHA_PUBLIC_KEY \
  -E CACHE_PREFIX:$CACHE_PREFIX \
  -E PANDASSO_SECRET:$PANDASSO_SECRET \
  -E PANDASSO_URL:$PANDASSO_URL \
  -V $VERSION \
  $DEPLOYMENT_CONFIG
