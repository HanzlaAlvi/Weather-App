from pathlib import Path

BASE_DIR = Path(__file__).parent

# API Configuration
API_KEY = "742ea15c539150b83db9c40b723660f8"  #your default 
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_QUALITY_URL = "http://api.openweathermap.org/data/2.5/air_pollution"
GEOCODING_URL = "http://api.openweathermap.org/geo/1.0/direct"

# Email Configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = "abc@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "abc@0334"  # Replace with your app password

# File Paths
SAVED_LOCATIONS = BASE_DIR / "data" / "saved_locations.json"
WEATHER_HISTORY = BASE_DIR / "data" / "weather_history.csv"
BACKUP_DIR = BASE_DIR / "data" / "backups"

# Assets Paths
ICON_DIR = BASE_DIR / "assets" / "icons"
BG_DIR = BASE_DIR / "assets" / "backgrounds"
STYLES_DIR = BASE_DIR / "assets" / "styles"

# Create directories if they don't exist
for dir_path in [ICON_DIR, BG_DIR, STYLES_DIR, BACKUP_DIR, WEATHER_HISTORY.parent]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Theme Configuration
THEMES = {
    "light": {
        "bg": "#f5f7fa",
        "fg": "#2c3e50",
        "card": "#ffffff",
        "accent": "#3498db",
        "text": "#333333"
    },
    "dark": {
        "bg": "#1a1a2e",
        "fg": "#e6e6e6",
        "card": "#16213e",
        "accent": "#4cc9f0",
        "text": "#ffffff"
    }
}