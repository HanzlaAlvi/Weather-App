import requests
from config import API_KEY, BASE_URL, FORECAST_URL, AIR_QUALITY_URL, GEOCODING_URL
from datetime import datetime
import time
from typing import Optional, Dict, List

class WeatherAPI:
    @staticmethod
    def get_coordinates(city: str) -> Optional[Dict]:
        """Get latitude and longitude for a city"""
        params = {
            "q": city,
            "limit": 1,
            "appid": API_KEY
        }
        try:
            response = requests.get(GEOCODING_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0] if data else None
        except:
            return None

    @staticmethod
    def get_weather(city: str, units: str = "metric") -> Optional[Dict]:
        """Get current weather data"""
        params = {
            "q": city,
            "appid": API_KEY,
            "units": units
        }
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except:
            return None

    @staticmethod
    def get_forecast(city: str, days: int = 5, units: str = "metric") -> Optional[Dict]:
        """Get weather forecast"""
        params = {
            "q": city,
            "appid": API_KEY,
            "units": units,
            "cnt": days * 8  # 3-hour intervals
        }
        try:
            response = requests.get(FORECAST_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except:
            return None

    @staticmethod
    def get_air_quality(lat: float, lon: float) -> Optional[Dict]:
        """Get air quality data"""
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY
        }
        try:
            response = requests.get(AIR_QUALITY_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except:
            return None

    @staticmethod
    def get_historical(lat: float, lon: float, date: datetime) -> Optional[Dict]:
        """Get historical weather data"""
        params = {
            "lat": lat,
            "lon": lon,
            "dt": int(date.timestamp()),
            "appid": API_KEY
        }
        try:
            response = requests.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except:
            return None