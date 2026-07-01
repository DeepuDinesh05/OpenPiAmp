#!/usr/bin/env bash
set -e

SERVICE_FILE=/etc/systemd/system/openpiamp.service

sudo systemctl disable --now openpiamp.service

if [ -f "$SERVICE_FILE" ]; then
    sudo rm "$SERVICE_FILE"
    sudo systemctl daemon-reload
fi

echo "openpiamp.service stopped, disabled, and removed."
