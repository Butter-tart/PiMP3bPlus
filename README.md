# PiMP3bPlus

A portable MP3 player built with Raspberry Pi 3B+, Waveshare 2.13-inch e-Ink V4 display, and 8BitDo Zero 2 Gamepad.

## Features
- MP3/WAV Playback.
- e-Ink display with 'Now Playing' screen.
- Gamepad navigation (8BitDo Zero 2).
- Settings menu and customizable volume.

## Hardware Requirements
- Raspberry Pi 3B+ (or similar).
- Waveshare 2.13inch e-Paper HAT (V4).
- 8BitDo Zero 2 Gamepad.
- MicroSD card with Raspberry Pi OS.
- 3.5mm Headphones or Bluetooth Speakers.

## Software Setup

### Quick Bring-Up (Recommended on Raspberry Pi)
Run this from the project folder on the Pi:
```bash
chmod +x pi_setup.sh
./pi_setup.sh
```
This script installs required packages, enables SPI, checks `/dev/spidev*`, and runs a real e-Ink draw test.

If SPI was just enabled, reboot once and run:
```bash
python3 check_hardware.py --draw-test
python3 main.py
```

### 1. Enable SPI
The e-Ink display requires SPI. Enable it via `raspi-config`:
```bash
sudo raspi-config
# Interfacing Options -> SPI -> Enable
```

### 2. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil python3-pygame python3-evdev python3-rpi.gpio python3-spidev
```
*Note: Using `apt-get` to install dependencies is recommended on Raspberry Pi OS to avoid compilation issues.*

### 3. Setup Gamepad
Pair your 8BitDo Zero 2 in **Android Mode** (Hold `B + START` to turn on, then `SELECT` for 3s to pair).
Verify the device appears in `/dev/input/`.

### 4. Hardware Driver
The project includes the official Waveshare driver in `lib/` (specifically for the 2.13inch V4 e-Paper). It requires `RPi.GPIO` and `spidev` to be installed (see Step 2). If these are missing, the application will automatically fall back to a simulation mode. 

To validate hardware link, run:
```bash
python3 check_hardware.py --draw-test
```

**Note on V4 Partial Refresh**: The V4 display supports fast partial refreshes. The application is configured to perform a full refresh every 20 cycles to maintain screen quality and clear any ghosting.

### 5. Add Music
Place your `.mp3` or `.wav` files in the `music/` directory.

## Usage
Run the main application:
```bash
python3 main.py
```

### Controls
- **D-Pad Up/Down**: Navigate menus.
- **D-Pad Left/Right**: Adjust volume.
- **A Button**: Select / Play / Pause.
- **B Button**: Back.

## Troubleshooting

### e-Ink falls back to simulation mode
1. Confirm SPI node exists:
```bash
ls -l /dev/spidev*
```
2. Confirm Python modules are installed:
```bash
python3 -c "import RPi.GPIO, spidev; print('ok')"
```
3. Run diagnostic for exact reason:
```bash
python3 check_hardware.py --draw-test
```

If `/dev/spidev0.0` is missing, enable SPI in `raspi-config` and reboot.

### Gamepad not found
1. Ensure controller is paired in Android mode.
2. Install evdev:
```bash
sudo apt-get install -y python3-evdev
```
3. Verify input devices:
```bash
ls /dev/input/event*
```
