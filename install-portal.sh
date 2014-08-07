#!/bin/bash
chmod 600 /opt/codeforlife-deploy/codeforlife-portal-rsa
ssh-add /opt/codeforlife-deploy/codeforlife-portal-rsa
pip install git+ssh://git@github.com/ocadotechnology/codeforlife-portal#egg=codeforlife-portal
