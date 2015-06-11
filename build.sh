#!/bin/bash
pip install -U -t lib -r requirements.txt
./install-portal.sh
./install-rapid-router.sh
echo "Following packages present:"
pip freeze
echo "--------------------------------------------------------------------------------"
