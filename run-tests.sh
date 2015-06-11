#!/bin/bash
cd /opt/codeforlife-deploy/
./build.sh
./manage.py test game.tests.passing