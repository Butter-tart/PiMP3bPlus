import time
import logging
import signal
import os
import threading
import config
from display_manager import DisplayManager
from input_manager import InputManager
from audio_player import AudioPlayer
from ui_manager import UIManager
from settings_manager import SettingsManager
from web_server import PiMP3WebServer

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PiMP3bPlus:
    def __init__(self):
        self.settings = SettingsManager(config.SETTINGS_FILE)
        self.settings.load()

        self.display = DisplayManager()
        self.audio = AudioPlayer()
        self.audio.set_volume(self.settings.get("volume", 0.7))

        self.ui = UIManager(
            self.display,
            self.audio,
            settings_manager=self.settings,
            exit_callback=self.stop,
        )
        self.input = InputManager()
        self.web = PiMP3WebServer(self, host=config.WEB_HOST, port=config.WEB_PORT)
        self.control_lock = threading.RLock()

        last_song = self.settings.get("last_song")
        if last_song:
            last_song_path = os.path.join(config.MUSIC_DIR, last_song)
            if os.path.exists(last_song_path):
                if self.audio.load_music(last_song_path):
                    logging.info(f"Preloaded last song: {last_song}")
        
        self.setup_inputs()
        self.running = True
        self._stopping = False

    def setup_inputs(self):
        # Button Mappings
        self.input.set_callback(config.BUTTON_A, lambda: self.handle_action("A"))
        self.input.set_callback(config.BUTTON_B, lambda: self.handle_action("B"))
        self.input.set_callback(config.BUTTON_SELECT, lambda: self.handle_action("SELECT"))
        self.input.set_callback(config.BUTTON_START, lambda: self.handle_action("START"))
        
        # D-Pad Mappings
        def handle_hat_x(value):
            if value == -1: # LEFT
                self.handle_action("LEFT")
            elif value == 1: # RIGHT
                self.handle_action("RIGHT")

        def handle_hat_y(value):
            if value == -1: # UP
                self.handle_action("UP")
            elif value == 1: # DOWN
                self.handle_action("DOWN")

        self.input.set_callback(config.ABS_HAT0X, handle_hat_x)
        self.input.set_callback(config.ABS_HAT0Y, handle_hat_y)

    def start(self):
        logging.info("Starting PiMP3bPlus...")
        self.web.start()
        input_started = self.input.start()
        if not input_started:
            logging.warning("Input device not active. Connect the gamepad to enable controls.")

        if not self.audio.available:
            logging.warning("Audio is unavailable. Check your output device and ALSA/Pulse configuration.")

        self.ui.draw() # Initial draw
        
        try:
            while self.running:
                with self.control_lock:
                    if self.audio.poll_song_finished():
                        self.ui.handle_song_finished()
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def handle_action(self, action):
        with self.control_lock:
            self.ui.handle_input(action)

    def get_web_status(self):
        with self.control_lock:
            status = self.audio.get_status()
            return {
                "song": status.get("song"),
                "playing": status.get("playing", False),
                "paused": status.get("paused", False),
                "volume": status.get("volume", 0.0),
                "audio_available": status.get("audio_available", False),
                "position_s": status.get("position_s", 0),
                "length_s": status.get("length_s", 0),
                "state": self.ui.state,
                "shuffle": self.ui.settings.get("Shuffle", False),
                "repeat": self.ui.settings.get("Repeat", False),
            }

    def get_web_songs(self):
        with self.control_lock:
            songs = self.audio.get_music_list()
            return {
                "songs": songs,
                "current_song": self.audio.current_song,
            }

    def handle_web_action(self, action, payload=None):
        payload = payload or {}
        action = (action or "").upper()

        with self.control_lock:
            try:
                if action == "PLAY_PAUSE":
                    if self.audio.current_song:
                        self.ui.handle_input("START")
                    else:
                        songs = self.audio.get_music_list()
                        if songs:
                            self.ui.play_song_by_name(songs[0])
                elif action == "NEXT":
                    self.audio.next_song(shuffle=self.ui.settings.get("Shuffle", False), use_forward_history=True)
                    self.ui.state = config.STATE_PLAYING
                    self.ui.draw()
                    self.ui.persist_runtime_state()
                elif action == "PREV":
                    self.audio.prev_song(shuffle=self.ui.settings.get("Shuffle", False))
                    self.ui.state = config.STATE_PLAYING
                    self.ui.draw()
                    self.ui.persist_runtime_state()
                elif action == "VOL_UP":
                    self.audio.set_volume(self.audio.volume + 0.1)
                    self.ui.persist_runtime_state()
                    self.ui.draw()
                elif action == "VOL_DOWN":
                    self.audio.set_volume(self.audio.volume - 0.1)
                    self.ui.persist_runtime_state()
                    self.ui.draw()
                elif action == "TOGGLE_SHUFFLE":
                    self.ui.set_setting("Shuffle", not self.ui.settings.get("Shuffle", False))
                elif action == "TOGGLE_REPEAT":
                    self.ui.set_setting("Repeat", not self.ui.settings.get("Repeat", False))
                elif action == "PLAY_SONG":
                    song = payload.get("song")
                    if not song or not self.ui.play_song_by_name(song):
                        return {"ok": False, "error": "Song not found or failed to play"}
                elif action in {"UP", "DOWN", "LEFT", "RIGHT", "A", "B", "SELECT", "START"}:
                    self.ui.handle_input(action)
                else:
                    return {"ok": False, "error": f"Unsupported action: {action}"}

                return {"ok": True, "status": self.get_web_status()}
            except Exception as e:
                logging.error(f"Web action failed ({action}): {e}")
                return {"ok": False, "error": str(e)}

    def stop(self):
        if self._stopping:
            return
        self._stopping = True

        logging.info("Stopping PiMP3bPlus...")
        self.ui.persist_runtime_state()
        self.running = False
        self.web.stop()
        self.input.stop()
        self.audio.stop()
        self.display.sleep()
        logging.info("PiMP3bPlus stopped.")

if __name__ == "__main__":
    player = PiMP3bPlus()
    
    # Handle signals for graceful shutdown
    signal.signal(signal.SIGINT, lambda s, f: player.stop())
    signal.signal(signal.SIGTERM, lambda s, f: player.stop())
    
    player.start()
