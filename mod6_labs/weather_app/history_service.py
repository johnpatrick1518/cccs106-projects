# history_service.py
import json
import os
from typing import List

HISTORY_FILE = "search_history.json"
MAX_HISTORY = 10  # you can change this if you want more saved searches


class HistoryService:
    """Handles saving and loading search history from a JSON file."""

    def __init__(self):
        self.file_path = HISTORY_FILE
        self.history: List[str] = []
        self._load_history()

    def _load_history(self):
        """Load search history from file, if it exists."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.history = data
            except (json.JSONDecodeError, IOError):
                # Corrupt or unreadable file → reset it
                self.history = []
        else:
            self.history = []

    def _save_history(self):
        """Write the current history to the file."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.history, f, indent=2)
        except IOError as e:
            print(f"Failed to save history: {e}")

    def add_city(self, city: str):
        """Add a city to the search history, avoiding duplicates."""
        if not city:
            return
        city = city.strip().title()
        if city in self.history:
            self.history.remove(city)
        self.history.insert(0, city)
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[:MAX_HISTORY]
        self._save_history()

    def get_history(self) -> List[str]:
        """Return the list of saved city names."""
        return self.history
