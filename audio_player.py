import pygame
import os
import config
import logging

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_song = None
        self.is_paused = False
        self.volume = 0.7
        pygame.mixer.music.set_volume(self.volume)

    def load_music(self, file_path):
        if os.path.exists(file_path):
            pygame.mixer.music.load(file_path)
            self.current_song = os.path.basename(file_path)
            self.is_paused = False
            return True
        return False

    def play(self):
        pygame.mixer.music.play()
        self.is_paused = False

    def pause_resume(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
        else:
            pygame.mixer.music.pause()
            self.is_paused = True

    def stop(self):
        pygame.mixer.music.stop()
        self.current_song = None

    def next_song(self):
        music_list = self.get_music_list()
        if not music_list:
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
        pygame.mixer.music.set_volume(self.volume)

    def get_status(self):
        return {
            "song": self.current_song,
            "playing": pygame.mixer.music.get_busy(),
            "paused": self.is_paused,
            "volume": self.volume
        }

    def get_music_list(self):
        if not os.path.exists(config.MUSIC_DIR):
            return []
        return [f for f in os.listdir(config.MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]
