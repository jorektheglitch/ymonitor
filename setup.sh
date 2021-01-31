#!/bin/bash

# Simple yggdrasil node monitoring
# https://github.com/jorektheglitch/ymonitor

mkdir -p /opt/ymonitor
cp -rf ./* /opt/ymonitor/
cd /opt/ymonitor

apt install python3-venv
python3 -m venv ./venv
./venv/bin/pip3 install -r requirements.txt

until [[ $CONTINUE =~ (y|n) ]]; do
    read -rp "Create a systemd units for webservice and background service? [y/n]: " -e CONTINUE
done
if [[ $CONTINUE == "y" ]]; then
    cp -f ./units/* /etc/systemd/system/
    systemctl daemon-reload
fi
