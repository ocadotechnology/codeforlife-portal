#!/bin/bash
./build.sh
./manage.py collectstatic --noinput
./manage.py test $1
