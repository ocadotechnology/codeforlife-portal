#!/bin/bash
pip install -U -t lib -r requirements.txt
./scripts/install-portal.sh
./scripts/install-rapid-router.sh
echo "Following packages present:"
ls -ltr lib | grep -v info
echo "--------------------------------------------------------------------------------"
