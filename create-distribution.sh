#!/bin/bash
./build.sh
./manage.py collectstatic --noinput
./manage.py compress -f
tar -cvzf distribution.tar.gz *