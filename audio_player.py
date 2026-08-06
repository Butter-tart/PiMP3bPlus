import pygame
import os
import config
import logging

class AudioPlayer:
    def __init__(self):
        self.available = False
        self.current_song = None
        self.is_paused = False
        self.volume = 0.7
        self._was_busy = False
        self._manual_stop = False

        try:
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.volume)
            self.available = True
            logging.info("Audio mixer initialized.")
        except Exception as e:
            logging.error(f"Audio mixer initialization failed: {e}")
            logging.warning("Audio playback is disabled until a valid output device is available.")

    def load_music(self, file_path):
        if not self.available:
            return False
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            self.current_song = os.path.basename(file_path)
            self.is_paused = False
            self._manual_stop = False
            self._was_busy = False
            return True
        return False

    def play(self):
        if not self.available:
            return
        pygame.mixer.music.play()
        self.is_paused = False
        self._manual_stop = False

    def pause_resume(self):
        if not self.available or not self.current_song:
            return
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop(self):
        if not self.available:
            self.current_song = None
            self.is_paused = False
            self._was_busy = False
            return
        self._manual_stop = True
        pygame.mixer.music.stop()
        self.current_song = None
        self.is_paused = False
        self._was_busy = False

    def next_song(self):
        music_list = self.get_music_list()
        if not music_list:
            self.stop()
            return
        
        if self.current_song in music_list:
            idx = music_list.index(self.current_song)
            next_idx = (idx + 1) % len(music_list)
        else:
            next_idx = 0
            
        self.load_music(os.path.join(config.MUSIC_DIR, music_list[next_idx]))
        self.play()

    def prev_song(self):
        music_list = self.get_music_list()
        if not music_list:
            self.stop()
            return
        
        if self.current_song in music_list:
            idx = music_list.index(self.current_song)
            prev_idx = (idx - 1) % len(music_list)
        else:
            prev_idx = 0
            
        self.load_music(os.path.join(config.MUSIC_DIR, music_list[prev_idx]))
        self.play()

    def set_volume(self, volume):
        self.volume = max(0.0, min(1.0, volume))
        if self.available:
            pygame.mixer.music.set_volume(self.volume)

    def poll_song_finished(self):
        if not self.available or not self.current_song:
            return False

        busy = pygame.mixer.music.get_busy()
        finished = self._was_busy and not busy and not self.is_paused and not self._manual_stop
        self._was_busy = busy

        if finished:
            self._manual_stop = False
        return finished

    def get_status(self):
        return {
            "song": self.current_song,
            "playing": pygame.mixer.music.get_busy() if self.available else False,
            "paused": self.is_paused,
            "volume": self.volume,
            "audio_available": self.available
        }

    def get_music_list(self):
        if not os.path.exists(config.MUSIC_DIR):
            return []
        return [f for f in os.listdir(config.MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
