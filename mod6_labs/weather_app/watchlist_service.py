# watchlist_service.py
import json
import os

WATCHLIST_FILE = "watchlist.json"

class WatchlistService:
    def __init__(self):
        self.file = WATCHLIST_FILE
        self.cities = self._load()

    def _load(self):
        if os.path.exists(self.file):
            try:
                with open(self.file, "r") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def save(self):
        with open(self.file, "w") as f:
            json.dump(self.cities, f)

    def add_city(self, city: str):
        city = city.strip().title()
        if city and city not in self.cities:
            self.cities.append(city)
            self.save()

    def remove_city(self, city: str):
        city = city.strip().title()
        if city in self.cities:
            self.cities.remove(city)
            self.save()

    def get_watchlist(self):
        return self.cities
