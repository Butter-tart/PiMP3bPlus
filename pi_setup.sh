#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "== PiMP3bPlus Pi setup =="
echo "Project: ${PROJECT_DIR}"

echo "[1/5] Updating apt index..."
sudo apt-get update

echo "[2/5] Installing system packages..."
sudo apt-get install -y \
  python3-pip \
  python3-pil \
  python3-pygame \
  python3-evdev \
  python3-rpi.gpio \
  python3-spidev

echo "[3/5] Enabling SPI..."
if command -v raspi-config >/dev/null 2>&1; then
  sudo raspi-config nonint do_spi 0 || true
else
  echo "raspi-config not found. Enable SPI manually in /boot config."
fi

echo "[4/5] Checking SPI device nodes..."
if ls /dev/spidev* >/dev/null 2>&1; then
  ls -l /dev/spidev*
else
  echo "SPI device nodes not found yet. Reboot required after enabling SPI."
fi

echo "[5/5] Running hardware diagnostic with draw test..."
cd "${PROJECT_DIR}"
python3 check_hardware.py --draw-test

echo "Setup complete. If SPI was just enabled, reboot and rerun:"
echo "  python3 check_hardware.py --draw-test"
echo "Then run:"
echo "  python3 main.py"
