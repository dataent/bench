#!/bin/bash -eux

# Install EPAAS
wget https://raw.githubusercontent.com/dataent/bench/master/playbooks/install.py
python install.py --production --user dataent --mysql-root-password dataent --admin-password admin