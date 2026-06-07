#!/bin/bash
echo "Installing Zuup Pad Sync Service..."

# 1. Install Udev rule to permanently bypass Permission Denied errors
sudo mkdir -p /etc/udev/rules.d
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="239a", MODE="0666"' | sudo tee /etc/udev/rules.d/99-zuup-pad.rules > /dev/null
echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="2886", MODE="0666"' | sudo tee -a /etc/udev/rules.d/99-zuup-pad.rules > /dev/null
sudo udevadm control --reload-rules
sudo udevadm trigger

# 2. Create Systemd Service for the background Sync Daemon
mkdir -p ~/.config/systemd/user
cat <<EOF > ~/.config/systemd/user/zuup-sync.service
[Unit]
Description=Zuup Pad Sync Daemon
After=network.target

[Service]
ExecStart=/usr/bin/python3 $(pwd)/desktop_app/sync.py
WorkingDirectory=$(pwd)
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

systemctl --user daemon-reload
systemctl --user enable zuup-sync.service
systemctl --user start zuup-sync.service

echo "Done! The Sync daemon is now permanently running in the background."
