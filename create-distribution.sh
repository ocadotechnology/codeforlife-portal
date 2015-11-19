#!/bin/bash
./build.sh
./manage.py collectstatic --noinput
tar -cvzf distribution.tar.gz *
