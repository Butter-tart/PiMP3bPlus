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

### 1. Enable SPI
The e-Ink display requires SPI. Enable it via `raspi-config`:
```bash
sudo raspi-config
# Interfacing Options -> SPI -> Enable
```

### 2. Install Dependencies
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-pil python3-pygame python3-evdev
```

### 3. Setup Gamepad
Pair your 8BitDo Zero 2 in **Android Mode** (Hold `B + START` to turn on, then `SELECT` for 3s to pair).
Verify the device appears in `/dev/input/`.

### 4. Install Waveshare Library
The project includes a mock for development, but for the real hardware, you should install the official Waveshare e-Paper library or place the `epd2in13_V4.py` and `epdconfig.py` in the `lib/` directory.

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
