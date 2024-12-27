#!/bin/bash

echo "**** installing python3 ****"
apk add --no-cache python3 py3-pip

echo "**** installing qbittorrent-api ****"
pip3 install qbittorrent-api --break-system-packages
