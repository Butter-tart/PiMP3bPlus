import time
import logging
import signal
import sys
import config
from display_manager import DisplayManager
from input_manager import InputManager
from audio_player import AudioPlayer
from ui_manager import UIManager

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PiMP3bPlus:
    def __init__(self):
        self.display = DisplayManager()
        self.audio = AudioPlayer()
        self.ui = UIManager(self.display, self.audio)
        self.input = InputManager()
        
        self.setup_inputs()
        self.running = True

    def setup_inputs(self):
        # Button Mappings
        self.input.set_callback(config.BUTTON_A, lambda: self.ui.handle_input("A"))
        self.input.set_callback(config.BUTTON_B, lambda: self.ui.handle_input("B"))
        self.input.set_callback(config.BUTTON_SELECT, lambda: self.ui.handle_input("SELECT"))
        self.input.set_callback(config.BUTTON_START, lambda: self.ui.handle_input("START"))
        
        # D-Pad Mappings
        def handle_hat_x(value):
            if value == -1: # LEFT
                self.ui.handle_input("LEFT")
            elif value == 1: # RIGHT
                self.ui.handle_input("RIGHT")

        def handle_hat_y(value):
            if value == -1: # UP
                self.ui.handle_input("UP")
            elif value == 1: # DOWN
                self.ui.handle_input("DOWN")

        self.input.set_callback(config.ABS_HAT0X, handle_hat_x)
        self.input.set_callback(config.ABS_HAT0Y, handle_hat_y)

    def start(self):
        logging.info("Starting PiMP3bPlus...")
        self.input.start()
        self.ui.draw() # Initial draw
        
        try:
            while self.running:
                # Main loop could handle things like screen sleep or updates
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        logging.info("Stopping PiMP3bPlus...")
        self.running = False
        self.input.stop()
        self.audio.stop()
        self.display.sleep()
        sys.exit(0)

if __name__ == "__main__":
    player = PiMP3bPlus()
    
    # Handle signals for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: player.stop())
    signal.signal(signal.SIGTERM, lambda s, f: player.stop())
    
    player.start()
