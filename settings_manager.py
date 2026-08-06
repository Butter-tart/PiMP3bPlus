import json
import logging
import os


class SettingsManager:
    DEFAULTS = {
        "shuffle": False,
        "repeat": False,
        "volume": 0.7,
        "audio_out": "3.5mm Jack",
        "last_song": None,
    }

    def __init__(self, file_path):
        self.file_path = file_path
        self.settings = dict(self.DEFAULTS)

    def load(self):
        if not os.path.exists(self.file_path):
            self.save()
            return self.settings

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            if isinstance(raw, dict):
                self.settings.update(raw)
        except Exception as e:
            logging.warning(f"Failed to load settings file {self.file_path}: {e}. Using defaults.")

        self._sanitize()
        return self.settings

    def save(self):
        self._sanitize()
        temp_path = f"{self.file_path}.tmp"
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, sort_keys=True)
            os.replace(temp_path, self.file_path)
        except Exception as e:
            logging.error(f"Failed to save settings file {self.file_path}: {e}")

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value, save=True):
        self.settings[key] = value
        self._sanitize()
        if save:
            self.save()

    def update(self, values, save=True):
        self.settings.update(values)
        self._sanitize()
        if save:
            self.save()

    def _sanitize(self):
        self.settings["shuffle"] = bool(self.settings.get("shuffle", False))
        self.settings["repeat"] = bool(self.settings.get("repeat", False))

        try:
            volume = float(self.settings.get("volume", 0.7))
        except Exception:
            volume = 0.7
        self.settings["volume"] = max(0.0, min(1.0, volume))

        audio_out = self.settings.get("audio_out", "3.5mm Jack")
        if audio_out not in ("3.5mm Jack", "Bluetooth"):
            audio_out = "3.5mm Jack"
        self.settings["audio_out"] = audio_out

        last_song = self.settings.get("last_song")
        self.settings["last_song"] = last_song if isinstance(last_song, str) and last_song else None
