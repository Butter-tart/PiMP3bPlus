import evdev
from evdev import ecodes
import config
import threading
import logging

class InputManager:
    def __init__(self, device_name="8BitDo Zero 2 gamepad"):
        self.device_name = device_name
        self.device = self._find_device()
        self.callbacks = {}
        self.running = False
        self._thread = None

    def _find_device(self):
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in devices:
            if self.device_name in device.name:
                logging.info(f"Found gamepad: {device.name} at {device.path}")
                return device
        logging.warning(f"Gamepad '{self.device_name}' not found.")
        return None

    def set_callback(self, event_code, callback):
        self.callbacks[event_code] = callback

    def start(self):
        if self.device:
            self.running = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False
        if self._thread:
            self._thread.join()

    def _run(self):
        try:
            for event in self.device.read_loop():
                if not self.running:
                    break
                
                # Check for button events (EV_KEY)
                if event.type == ecodes.EV_KEY:
                    if event.code in self.callbacks and event.value == 1: # Button Pressed
                        self.callbacks[event.code]()
                
                # Check for D-pad events (EV_ABS for Hat)
                elif event.type == ecodes.EV_ABS:
                    if event.code in self.callbacks:
                        # For Hat events, value is -1, 0, or 1
                        self.callbacks[event.code](event.value)
                        
        except Exception as e:
            logging.error(f"Input thread error: {e}")
            self.running = False
