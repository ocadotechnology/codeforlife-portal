#!/bin/bash
./build.sh
./manage.py collectstatic --noinput
./manage.py compress -f
zip -r lib lib/*
tar -cvzf distribution.tar.gz *