import config

class UIManager:
    def __init__(self, display_manager, audio_player):
        self.display = display_manager
        self.audio = audio_player
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
        self.settings_keys = list(self.settings.keys())

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
        status = self.audio.get_status()
        self.display.draw_text(10, 5, "Now Playing", font_size="large")
        song_name = status["song"] if status["song"] else "None"
        self.display.draw_text(10, 40, song_name, font_size="medium")
        
        state_text = "Paused" if status["paused"] else "Playing"
        self.display.draw_text(10, 70, f"Status: {state_text}")
        self.display.draw_text(10, 90, f"Volume: {int(status['volume'] * 100)}%")

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
            self.current_menu_index = min(limit - 1, self.current_menu_index + 1)
        elif action == "LEFT":
            if self.state == config.STATE_PLAYING:
                self.audio.prev_song()
            else:
                self.audio.set_volume(self.audio.volume - 0.1)
        elif action == "RIGHT":
            if self.state == config.STATE_PLAYING:
                self.audio.next_song()
            else:
                self.audio.set_volume(self.audio.volume + 0.1)
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
                    import sys
                    sys.exit(0)
            elif self.sub_menu_type == "MUSIC_LIST":
                if self.music_list:
                    song = self.music_list[self.current_menu_index]
                    import os
                    if self.audio.load_music(os.path.join(config.MUSIC_DIR, song)):
                        self.audio.play()
                        self.state = config.STATE_PLAYING
                        self.draw(full_refresh=True)
            elif self.sub_menu_type == "SETTINGS":
                key = self.settings_keys[self.current_menu_index]
                if key == "Audio Out":
                    self.settings[key] = "Bluetooth" if self.settings[key] == "3.5mm Jack" else "3.5mm Jack"
                else:
                    self.settings[key] = not self.settings[key]
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
