import config
import os

class UIManager:
    def __init__(self, display_manager, audio_player, settings_manager=None, exit_callback=None):
        self.display = display_manager
        self.audio = audio_player
        self.settings_manager = settings_manager
        self.exit_callback = exit_callback
        self.state = config.STATE_MENU
        self.menu_items = ["Play Music", "Settings", "Exit"]
        self.current_menu_index = 0
        self.music_list = []
        self.in_sub_menu = False
        self.sub_menu_type = None # "MUSIC_LIST" or "SETTINGS"
        
        # Settings
        self.settings = {
            "Shuffle": False,
            "Repeat": False,
            "Audio Out": "3.5mm Jack"
        }
        if self.settings_manager is not None:
            self.settings["Shuffle"] = self.settings_manager.get("shuffle", False)
            self.settings["Repeat"] = self.settings_manager.get("repeat", False)
            self.settings["Audio Out"] = self.settings_manager.get("audio_out", "3.5mm Jack")

        self.settings_keys = list(self.settings.keys())

    def _persist_settings(self):
        if self.settings_manager is None:
            return
        self.settings_manager.update(
            {
                "shuffle": self.settings["Shuffle"],
                "repeat": self.settings["Repeat"],
                "audio_out": self.settings["Audio Out"],
                "volume": self.audio.volume,
                "last_song": self.audio.current_song,
            },
            save=True,
        )

    def persist_runtime_state(self):
        self._persist_settings()

    def set_setting(self, key, value):
        if key not in self.settings:
            return False
        self.settings[key] = value
        self._persist_settings()
        self.draw()
        return True

    def play_song_by_name(self, song_name):
        if not song_name:
            return False
        self.update_music_list()
        if song_name not in self.music_list:
            return False
        if self.audio.play_song(song_name):
            self.state = config.STATE_PLAYING
            self._persist_settings()
            self.draw(full_refresh=True)
            return True
        return False

    def update_music_list(self):
        self.music_list = self.audio.get_music_list()

    def draw(self, full_refresh=False):
        self.display.clear()
        
        if self.state == config.STATE_MENU:
            if not self.in_sub_menu:
                self._draw_main_menu()
            elif self.sub_menu_type == "MUSIC_LIST":
                self._draw_music_list()
            elif self.sub_menu_type == "SETTINGS":
                self._draw_settings()
                
        elif self.state == config.STATE_PLAYING:
            self._draw_now_playing()
            
        self.display.display(partial=not full_refresh)

    def _draw_main_menu(self):
        self.display.draw_text(10, 5, "PiMP3bPlus", font_size="large")
        for i, item in enumerate(self.menu_items):
            prefix = "> " if i == self.current_menu_index else "  "
            self.display.draw_text(10, 35 + (i * 20), f"{prefix}{item}")

    def _draw_music_list(self):
        self.display.draw_text(10, 5, "Select Song", font_size="large")
        if not self.music_list:
            self.display.draw_text(10, 40, "No music found in /music")
            return

        # Show a window of 4 songs
        start_index = max(0, min(self.current_menu_index - 1, len(self.music_list) - 4))
        for i in range(start_index, min(start_index + 4, len(self.music_list))):
            prefix = "> " if i == self.current_menu_index else "  "
            song_name = self.music_list[i][:25] # Truncate long names
            self.display.draw_text(10, 35 + ((i - start_index) * 20), f"{prefix}{song_name}")

    def _draw_now_playing(self):
        def format_mmss(total_seconds):
            total_seconds = max(0, int(total_seconds))
            return f"{total_seconds // 60:02d}:{total_seconds % 60:02d}"

        status = self.audio.get_status()
        self.display.draw_text(10, 5, "Now Playing", font_size="large")
        song_name = status["song"] if status["song"] else "None"
        self.display.draw_text(10, 40, song_name, font_size="medium")
        
        state_text = "Paused" if status["paused"] else "Playing"
        self.display.draw_text(10, 70, f"Status: {state_text}")
        self.display.draw_text(10, 90, f"Volume: {int(status['volume'] * 100)}%", font_size="small")

        pos = status.get("position_s", 0)
        length = status.get("length_s", 0)
        if length > 0:
            self.display.draw_text(95, 90, f"{format_mmss(pos)}/{format_mmss(length)}", font_size="small")

            bar_x, bar_y, bar_w, bar_h = 10, 108, 220, 8
            self.display.draw.rectangle((bar_x, bar_y, bar_x + bar_w, bar_y + bar_h), outline=0, fill=255)
            progress = min(1.0, max(0.0, pos / max(1, length)))
            fill_w = int(bar_w * progress)
            if fill_w > 0:
                self.display.draw.rectangle((bar_x + 1, bar_y + 1, bar_x + fill_w - 1, bar_y + bar_h - 1), fill=0)

        if not status.get("audio_available", True):
            self.display.draw_text(140, 90, "Audio OFF", font_size="small")

    def _draw_settings(self):
        self.display.draw_text(10, 5, "Settings", font_size="large")
        for i, key in enumerate(self.settings_keys):
            prefix = "> " if i == self.current_menu_index else "  "
            value = self.settings[key]
            if isinstance(value, bool):
                value_str = "ON" if value else "OFF"
            else:
                value_str = value
            self.display.draw_text(10, 35 + (i * 20), f"{prefix}{key}: {value_str}")
        self.display.draw_text(10, 105, "Press B to go back", font_size="small")

    def handle_input(self, action, value=None):
        if action == "UP":
            self.current_menu_index = max(0, self.current_menu_index - 1)
        elif action == "DOWN":
            if self.in_sub_menu:
                if self.sub_menu_type == "MUSIC_LIST":
                    limit = len(self.music_list)
                elif self.sub_menu_type == "SETTINGS":
                    limit = len(self.settings_keys)
                else:
                    limit = 1
            else:
                limit = len(self.menu_items)
            if limit > 0:
                self.current_menu_index = min(limit - 1, self.current_menu_index + 1)
            else:
                self.current_menu_index = 0
        elif action == "LEFT":
            if self.state == config.STATE_PLAYING:
                self.audio.prev_song(shuffle=self.settings.get("Shuffle", False))
            else:
                self.audio.set_volume(self.audio.volume - 0.1)
                self._persist_settings()
        elif action == "RIGHT":
            if self.state == config.STATE_PLAYING:
                if self.settings.get("Shuffle", False):
                    self.audio.next_song(shuffle=True, use_forward_history=True)
                else:
                    self.audio.next_song(shuffle=False)
            else:
                self.audio.set_volume(self.audio.volume + 0.1)
                self._persist_settings()
        elif action == "A":
            self._handle_select()
        elif action == "B":
            self._handle_back()
        elif action == "SELECT":
            # Direct access to settings or something else?
            pass
        elif action == "START":
            # Play/Pause from anywhere?
            if self.state == config.STATE_PLAYING or self.audio.current_song:
                self.audio.pause_resume()
                if self.state != config.STATE_PLAYING:
                    self.state = config.STATE_PLAYING
                    self.draw(full_refresh=True)
                else:
                    self.draw()
        
        # Determine if we need a full refresh
        # (e.g., when changing states or sub-menus)
        self.draw()

    def _handle_select(self):
        if self.state == config.STATE_MENU:
            if not self.in_sub_menu:
                if self.current_menu_index == 0: # Play Music
                    self.update_music_list()
                    self.in_sub_menu = True
                    self.sub_menu_type = "MUSIC_LIST"
                    self.current_menu_index = 0
                    self.draw(full_refresh=True)
                elif self.current_menu_index == 1: # Settings
                    self.in_sub_menu = True
                    self.sub_menu_type = "SETTINGS"
                    self.current_menu_index = 0
                    self.draw(full_refresh=True)
                elif self.current_menu_index == 2: # Exit
                    if self.exit_callback:
                        self.exit_callback()
            elif self.sub_menu_type == "MUSIC_LIST":
                if self.music_list and self.current_menu_index < len(self.music_list):
                    song = self.music_list[self.current_menu_index]
                    if self.audio.load_music(os.path.join(config.MUSIC_DIR, song)):
                        self.audio.play()
                        self._persist_settings()
                        self.state = config.STATE_PLAYING
                        self.draw(full_refresh=True)
            elif self.sub_menu_type == "SETTINGS":
                key = self.settings_keys[self.current_menu_index]
                if key == "Audio Out":
                    self.settings[key] = "Bluetooth" if self.settings[key] == "3.5mm Jack" else "3.5mm Jack"
                else:
                    self.settings[key] = not self.settings[key]
                self._persist_settings()
                self.draw()
        elif self.state == config.STATE_PLAYING:
            self.audio.pause_resume()
            self.draw()

    def _handle_back(self):
        if self.state == config.STATE_PLAYING:
            self.state = config.STATE_MENU
            self.draw(full_refresh=True)
        elif self.in_sub_menu:
            self.in_sub_menu = False
            self.sub_menu_type = None
            self.current_menu_index = 0
            self.draw(full_refresh=True)

    def handle_song_finished(self):
        if self.state == config.STATE_PLAYING:
            if self.settings.get("Repeat", False):
                self.audio.replay_current()
            elif self.settings.get("Shuffle", False):
                self.audio.next_song(shuffle=True, use_forward_history=False)
            else:
                self.audio.next_song(shuffle=False)
            self._persist_settings()
            self.draw()
