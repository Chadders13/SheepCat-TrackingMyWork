"""
Settings manager for SheepCat Work Tracker.

Loads and saves application settings to a JSON config file.
"""
import json
import os
import datetime


DEFAULT_SETTINGS = {
    "ollama_url": "http://localhost:11434/api/generate",
    "ollama_model": "deepseek-r1:8b",
    "checkin_interval_minutes": 60,
    "log_file_directory": ".",
    "log_file_name": "work_log",
    "log_file_date_format": "",  # e.g. "{yyyyMMdd}" - empty means no date in filename
    "llm_request_timeout": 1000,
    "max_chunk_size": 4000,
}

SETTINGS_FILE = "sheepcat_settings.json"

# Mapping from user-facing format tokens to Python strftime strings
DATE_FORMAT_MAP = {
    "{yyyyMMdd}": "%Y%m%d",
    "{ddmmyyyy}": "%d%m%Y",
    "{ddmmyy}": "%d%m%y",
    "{MMddyyyy}": "%m%d%Y",
    "{yyyyddMM}": "%Y%d%m",
    "{yyyy-MM-dd}": "%Y-%m-%d",
    "{dd-MM-yyyy}": "%d-%m-%Y",
}


class SettingsManager:
    """Manages application settings with persistence to a JSON file."""

    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = dict(DEFAULT_SETTINGS)
        self.load()

    def load(self):
        """Load settings from JSON file, using defaults for missing keys."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                for key in DEFAULT_SETTINGS:
                    if key in saved:
                        self.settings[key] = saved[key]
            except Exception as e:
                print(f"Error loading settings: {e}")

    def save(self):
        """Save current settings to JSON file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False

    def get(self, key, default=None):
        """Get a setting value by key."""
        if default is not None:
            return self.settings.get(key, default)
        return self.settings.get(key, DEFAULT_SETTINGS.get(key))

    def set(self, key, value):
        """Set a setting value."""
        self.settings[key] = value

    def get_log_file_path(self):
        """Build the full log file path with optional date format applied to the filename."""
        directory = self.settings.get("log_file_directory", ".")
        name = self.settings.get("log_file_name", "work_log")
        date_format = self.settings.get("log_file_date_format", "")

        if date_format and date_format in DATE_FORMAT_MAP:
            py_fmt = DATE_FORMAT_MAP[date_format]
            date_str = datetime.datetime.now().strftime(py_fmt)
            filename = f"{name}_{date_str}.csv"
        else:
            filename = f"{name}.csv"

        return os.path.join(directory, filename)
