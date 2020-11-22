# About
Simple monitoring service for Yggdrasil. 
Contains two parts: background service and web service.

Background service periodically asks Yggdrasil API for current node's coords and logs into db if it was changed.

Web service provides simple web page with log's summary.

# Installation

Running commands below do the installation (in directory /opt/ymonitor/).

```git clone https://github.com/jorektheglitch/ymonitor.git
cd ./ymonitor/
chmod +x setup.sh
sudo ./setup.sh```
