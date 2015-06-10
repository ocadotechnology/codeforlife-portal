#!/bin/bash
pip install -r requirements.txt
ssh-agent ./install-portal.sh
ssh-agent ./install-rapid-router.sh
echo "Following packages present:"
pip freeze
echo "--------------------------------------------------------------------------------"
