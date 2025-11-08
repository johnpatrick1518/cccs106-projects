# weather_service.py
import httpx
from typing import Dict
from config import Config


class WeatherServiceError(Exception):
    """Base custom exception for weather service errors."""
    pass


class WeatherService:
    """Handles API communication with OpenWeatherMap."""

    def __init__(self):
        self.api_key = Config.API_KEY
        self.base_url = Config.BASE_URL
        self.timeout = Config.TIMEOUT

    async def get_weather(self, city: str) -> Dict:
        """Fetch current weather for a given city."""
        if not city:
            raise WeatherServiceError("City name cannot be empty.")

        # basic character validation (letters, spaces, dashes)
        if not all(ch.isalpha() or ch.isspace() or ch in "-'" for ch in city):
            raise WeatherServiceError("Invalid characters in city name.")

        params = {"q": city.strip(), "appid": self.api_key, "units": Config.UNITS}
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.base_url, params=params)

                # Handle known status codes
                if response.status_code == 401:
                    raise WeatherServiceError("401: Invalid API key.")
                elif response.status_code == 404:
                    raise WeatherServiceError(f"404: City '{city}' not found.")
                elif response.status_code >= 500:
                    raise WeatherServiceError("Server error. Try again later.")

                response.raise_for_status()
                return response.json()

        except httpx.TimeoutException:
            raise WeatherServiceError("Request timed out. Check your connection.")
        except httpx.ConnectError:
            raise WeatherServiceError("Connection error. Please check your internet.")
        except httpx.NetworkError:
            raise WeatherServiceError("Network error occurred.")
        except httpx.RequestError as e:
            raise WeatherServiceError(f"Request error: {str(e)}")
        except Exception as e:
            raise WeatherServiceError(f"Unexpected error: {str(e)}")

    async def get_forecast(self, city: str) -> Dict:
        """Get 5-day weather forecast."""
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": Config.UNITS,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(forecast_url, params=params)
            response.raise_for_status()
            return response.json()
