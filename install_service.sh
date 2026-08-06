#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="pimp3bplus"
SERVICE_PATH="/etc/systemd/system/${SERVICE_NAME}.service"
RUN_USER="${SUDO_USER:-$USER}"
PYTHON_BIN="/usr/bin/python3"

if [[ ! -x "${PYTHON_BIN}" ]]; then
  echo "${PYTHON_BIN} not found. Install system python3 first."
  exit 1
fi

echo "Installing ${SERVICE_NAME}.service for user ${RUN_USER}"

sudo tee "${SERVICE_PATH}" >/dev/null <<EOF
[Unit]
Description=PiMP3bPlus MP3 Player
After=network.target sound.target

[Service]
Type=simple
User=${RUN_USER}
WorkingDirectory=${PROJECT_DIR}
ExecStart=${PYTHON_BIN} ${PROJECT_DIR}/main.py
Restart=always
RestartSec=3
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable "${SERVICE_NAME}.service"
sudo systemctl restart "${SERVICE_NAME}.service"

echo "Service installed and started."
echo "Check status with: sudo systemctl status ${SERVICE_NAME}.service"
echo "View logs with: sudo journalctl -u ${SERVICE_NAME}.service -f"
