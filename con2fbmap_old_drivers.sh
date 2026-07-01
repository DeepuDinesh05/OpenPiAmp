sudo tee /etc/systemd/system/con2fbmap.service > /dev/null <<'EOF'

[Unit]
Description=Map console to TFT framebuffer
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/con2fbmap 1 1
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable con2fbmap.service
