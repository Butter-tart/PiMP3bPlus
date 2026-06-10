import logging
import sys
import os

# Configure logging to see the output clearly
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_hardware():
    print("--- PiMP3bPlus Hardware Diagnostic ---")
    
    # 1. Check for libraries
    print("\n1. Checking Python Libraries:")
    try:
        import RPi.GPIO as GPIO
        print(" [OK] RPi.GPIO is installed.")
    except ImportError:
        print(" [FAIL] RPi.GPIO is NOT installed. Run: sudo apt-get install python3-rpi.gpio")

    try:
        import spidev
        print(" [OK] spidev is installed.")
    except ImportError:
        print(" [FAIL] spidev is NOT installed. Run: sudo apt-get install python3-spidev")

    try:
        import evdev
        print(" [OK] evdev is installed.")
    except ImportError:
        print(" [FAIL] evdev is NOT installed. Run: sudo apt-get install python3-evdev")

    # 2. Check for SPI
    print("\n2. Checking SPI Interface:")
    if os.path.exists("/dev/spidev0.0"):
        print(" [OK] SPI device /dev/spidev0.0 found.")
    else:
        print(" [FAIL] SPI device NOT found. Enable it in sudo raspi-config (Interfacing Options -> SPI)")

    # 3. Check for Project Files
    print("\n3. Checking Project Driver Files:")
    files = ["lib/epd2in13_V4.py", "lib/epdconfig.py"]
    for f in files:
        if os.path.exists(f):
            print(f" [OK] {f} found.")
        else:
            print(f" [FAIL] {f} is MISSING!")

    # 4. Attempt Display Initialization
    print("\n4. Attempting e-Ink Display Initialization:")
    sys.path.append(os.getcwd())
    try:
        from display_manager import DisplayManager
        dm = DisplayManager()
        if dm.epd is not None:
            print(" [SUCCESS] Display hardware initialized correctly!")
        else:
            print(" [INFO] DisplayManager is running in SIMULATION mode (no hardware detected).")
    except Exception as e:
        print(f" [ERROR] Initialization failed: {e}")

    print("\n---------------------------------------")

if __name__ == "__main__":
    check_hardware()
