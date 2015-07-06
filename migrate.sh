#!/bin/bash
# To be used to docker deployment environment
export DEPLOYMENT=1
./manage.py migrate
MIGRATERESULT=$?
if [ $MIGRATERESULT -ne 0 ]; then
  echo "Migrations failed"
  exit 1
fi
