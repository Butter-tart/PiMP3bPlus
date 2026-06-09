import os
import pygame
import time

# Create dummy music file
os.makedirs('music', exist_ok=True)
with open('music/test_song.mp3', 'wb') as f:
    f.write(b'\x00' * 1024)

# Test AudioPlayer
from audio_player import AudioPlayer
try:
    player = AudioPlayer()
    print("AudioPlayer initialized.")
    songs = player.get_music_list()
    print(f"Songs found: {songs}")
except Exception as e:
    print(f"AudioPlayer test failed (expected if SDL not present): {e}")

# Test DisplayManager
from display_manager import DisplayManager
try:
    dm = DisplayManager()
    dm.draw_text(10, 10, "Test Screen")
    dm.display()
    print("DisplayManager test passed.")
except Exception as e:
    print(f"DisplayManager test failed: {e}")

# Test UI Manager
from ui_manager import UIManager
try:
    # Need a mock audio player for UI test if pygame failed
    class MockAudio:
        def get_music_list(self): return ["song1.mp3", "song2.wav"]
        def get_status(self): return {"song": "song1.mp3", "playing": True, "paused": False, "volume": 0.5}
        def set_volume(self, v): self.volume = v
        def load_music(self, f): return True
        def play(self): pass
        def pause_resume(self): pass

    ui = UIManager(dm, MockAudio())
    ui.draw()
    print("UI Manager draw test passed.")
    ui.handle_input("DOWN")
    print("UI Manager input test passed.")
except Exception as e:
    print(f"UI Manager test failed: {e}")
