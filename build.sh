#!/bin/bash
pip install -r /opt/codeforlife-deploy/requirements.txt
pip install https://www.reportlab.com/pypi/packages/reportlab-3.1.47.tar.gz
ssh-agent /opt/codeforlife-deploy/install-portal.sh
ssh-agent /opt/codeforlife-deploy/install-rapid-router.sh
echo "Following packages present:"
pip freeze
echo "--------------------------------------------------------------------------------"
