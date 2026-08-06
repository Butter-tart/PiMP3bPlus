import pygame
import os
import random
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
        self._track_length_cache = {}
        self._back_history = []
        self._forward_history = []
        self._history_limit = 50

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
            try:
                pygame.mixer.music.load(file_path)
                self.current_song = os.path.basename(file_path)
                self.is_paused = False
                self._manual_stop = False
                self._was_busy = False
                return True
            except Exception as e:
                logging.error(f"Failed to load audio file {file_path}: {e}")
        return False

    def _remember_current_for_back(self):
        if not self.current_song:
            return
        self._back_history.append(self.current_song)
        if len(self._back_history) > self._history_limit:
            self._back_history = self._back_history[-self._history_limit:]

    def play(self):
        if not self.available:
            return False
        pygame.mixer.music.play()
        self.is_paused = False
        self._manual_stop = False
        self._was_busy = True
        return True

    def play_song(self, song_name):
        return self._play_song_internal(song_name, remember_current=False, clear_forward=False)

    def _play_song_internal(self, song_name, remember_current=True, clear_forward=True):
        file_path = os.path.join(config.MUSIC_DIR, song_name)
        if remember_current and self.current_song and self.current_song != song_name:
            self._remember_current_for_back()
        if clear_forward:
            self._forward_history.clear()
        if self.load_music(file_path):
            return self.play()
        return False

    def play_random_song(self, exclude_current=True):
        music_list = self.get_music_list()
        if not music_list:
            self.stop()
            return False

        candidates = music_list
        if exclude_current and self.current_song in music_list and len(music_list) > 1:
            candidates = [song for song in music_list if song != self.current_song]

        song = random.choice(candidates)
        return self._play_song_internal(song, remember_current=True, clear_forward=True)

    def replay_current(self):
        if not self.current_song:
            return False
        return self._play_song_internal(self.current_song, remember_current=False, clear_forward=False)

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

    def next_song(self, shuffle=False, use_forward_history=True):
        if shuffle:
            if use_forward_history and self._forward_history:
                target = self._forward_history.pop()
                return self._play_song_internal(target, remember_current=True, clear_forward=False)
            return self.play_random_song(exclude_current=True)

        music_list = self.get_music_list()
        if not music_list:
            self.stop()
            return False
        
        if self.current_song in music_list:
            idx = music_list.index(self.current_song)
            next_idx = (idx + 1) % len(music_list)
        else:
            next_idx = 0
            
        return self._play_song_internal(music_list[next_idx], remember_current=True, clear_forward=True)

    def prev_song(self, shuffle=False):
        if shuffle and self._back_history:
            target = self._back_history.pop()
            if self.current_song:
                self._forward_history.append(self.current_song)
            return self._play_song_internal(target, remember_current=False, clear_forward=False)

        music_list = self.get_music_list()
        if not music_list:
            self.stop()
            return False
        
        if self.current_song in music_list:
            idx = music_list.index(self.current_song)
            prev_idx = (idx - 1) % len(music_list)
        else:
            prev_idx = 0
            
        return self._play_song_internal(music_list[prev_idx], remember_current=True, clear_forward=True)

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

    def get_track_position_seconds(self):
        if not self.available or not self.current_song:
            return 0
        position_ms = pygame.mixer.music.get_pos()
        if position_ms < 0:
            return 0
        return int(position_ms / 1000)

    def get_track_length_seconds(self, song_name=None):
        song = song_name or self.current_song
        if not song:
            return 0
        if song in self._track_length_cache:
            return self._track_length_cache[song]

        file_path = os.path.join(config.MUSIC_DIR, song)
        if not os.path.exists(file_path):
            return 0

        try:
            length = int(pygame.mixer.Sound(file_path).get_length())
            self._track_length_cache[song] = max(0, length)
            return self._track_length_cache[song]
        except Exception:
            return 0

    def get_status(self):
        length_s = self.get_track_length_seconds(self.current_song)
        position_s = self.get_track_position_seconds()
        if length_s > 0:
            position_s = min(position_s, length_s)

        return {
            "song": self.current_song,
            "playing": pygame.mixer.music.get_busy() if self.available else False,
            "paused": self.is_paused,
            "volume": self.volume,
            "audio_available": self.available,
            "position_s": position_s,
            "length_s": length_s
        }

    def get_music_list(self):
        if not os.path.exists(config.MUSIC_DIR):
            return []
        return sorted([f for f in os.listdir(config.MUSIC_DIR) if f.endswith(('.mp3', '.wav'))])
