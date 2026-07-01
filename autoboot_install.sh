#!/usr/bin/env bash
set -e

RUN_USER="$(whoami)"
RUN_SCRIPT="$HOME/OpenPiAmp/run.sh"
WORKDIR="$HOME/OpenPiAmp"
SERVICE_FILE=/etc/systemd/system/openpiamp.service

if [ "$RUN_USER" = "root" ]; then
    echo "Don't run this installer with sudo/as root - run it as your normal user"
    echo "(it needs \$HOME and \$(whoami) to resolve to YOUR account, not root's)."
    exit 1
fi

if [ ! -f "$RUN_SCRIPT" ]; then
    echo "Expected $RUN_SCRIPT to exist - create it first (see run.sh from earlier)."
    exit 1
fi

sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=OpenPiAmp
After=multi-user.target

[Service]
Type=simple
User=$RUN_USER
WorkingDirectory=$WORKDIR
ExecStart=/bin/bash $RUN_SCRIPT
Restart=on-failure
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openpiamp.service

echo "Installed and enabled openpiamp.service - it will start automatically on next boot."
echo "Start it right now without rebooting: sudo systemctl start openpiamp.service"
echo "Check status/logs: systemctl status openpiamp.service  /  journalctl -u openpiamp.service -f"
