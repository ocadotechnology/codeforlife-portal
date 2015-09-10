#!/bin/bash
curl -s http://metadata/computeMetadata/v1/instance/service-accounts/default/token
ON_GOOGLE=$?
if (( ! $ON_GOOGLE )); then
  cd /tmp
  curl -s https://www.googleapis.com/storage/v1/b/decent-digit-629.appspot.com/o/django-pandasso-1.7.1.tar.gz?alt=media \
    -H "Authorization":"Bearer $(curl -s "http://metadata/computeMetadata/v1/instance/service-accounts/default/token" -H "Metadata-Flavor: Google" | jq -r .access_token)" > django-pandasso-1.7.1.tar.gz
  pip install -U -t lib django-pandasso-1.7.1.tar.gz
  cd -
fi
