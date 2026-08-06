import logging
import sys
import os
import argparse
import time
import config

# Configure logging to see the output clearly
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def check_hardware(draw_test=False):
    print("--- PiMP3bPlus Hardware Diagnostic ---")
    project_root = config.PROJECT_ROOT
    print(f"Project root: {project_root}")
    
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
    files = [
        os.path.join(project_root, "lib", "epd2in13_V4.py"),
        os.path.join(project_root, "lib", "epdconfig.py")
    ]
    for f in files:
        if os.path.exists(f):
            print(f" [OK] {f} found.")
        else:
            print(f" [FAIL] {f} is MISSING!")

    # 4. Attempt Display Initialization
    print("\n4. Attempting e-Ink Display Initialization:")
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    try:
        from display_manager import DisplayManager
        dm = DisplayManager()
        if dm.is_hardware_active():
            print(" [SUCCESS] Display hardware initialized correctly!")
            if draw_test:
                print("\n5. Running e-Ink draw test:")
                try:
                    dm.clear()
                    dm.draw_text(10, 10, "PiMP3bPlus")
                    dm.draw_text(10, 35, "e-Ink link test")
                    dm.draw_text(10, 60, "If you can read this,")
                    dm.draw_text(10, 85, "display path is working")
                    dm.display(partial=False)
                    print(" [SUCCESS] Draw test sent to panel.")
                    print(" [INFO] Waiting 2s before sleep...")
                    time.sleep(2)
                    dm.sleep()
                except Exception as e:
                    print(f" [ERROR] Draw test failed: {e}")
        else:
            print(" [INFO] DisplayManager is running in SIMULATION mode.")
            if getattr(dm, "simulation_reason", None):
                print(f" [DETAIL] Reason: {dm.simulation_reason}")
            print(" [HINT] Ensure python3-rpi.gpio and python3-spidev are installed and SPI is enabled.")
    except Exception as e:
        print(f" [ERROR] Initialization failed: {e}")

    print("\n---------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PiMP3bPlus hardware diagnostic")
    parser.add_argument(
        "--draw-test",
        action="store_true",
        help="Attempt a real draw to the e-Ink panel after successful initialization"
    )
    args = parser.parse_args()

    check_hardware(draw_test=args.draw_test)
