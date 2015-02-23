#!/bin/bash
chmod 600 /opt/codeforlife-deploy/ocargo-rsa
ssh-add /opt/codeforlife-deploy/ocargo-rsa
pip install git+ssh://git@github.com/ocadotechnology/ocargo#egg=ocargo
