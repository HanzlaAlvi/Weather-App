import json
import pandas as pd
from pathlib import Path
from config import SAVED_LOCATIONS, WEATHER_HISTORY, BACKUP_DIR
from datetime import datetime
from zipfile import ZipFile

class DataHandler:
    @staticmethod
    def init_files():
        """Initialize all required files and directories"""
        try:
            WEATHER_HISTORY.parent.mkdir(parents=True, exist_ok=True)
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            
            if not SAVED_LOCATIONS.exists():
                with open(SAVED_LOCATIONS, 'w', encoding='utf-8') as f:
                    json.dump({"locations": []}, f)
            
            if not WEATHER_HISTORY.exists():
                pd.DataFrame(columns=[
                    "city", "temp", "humidity", "conditions", 
                    "pressure", "wind_speed", "visibility", "timestamp"
                ]).to_csv(WEATHER_HISTORY, index=False)
        except Exception as e:
            print(f"Initialization error: {e}")

    @staticmethod
    def save_location(city: str):
        """Save favorite location with error handling"""
        try:
            DataHandler.init_files()
            with open(SAVED_LOCATIONS, 'r+', encoding='utf-8') as f:
                data = json.load(f)
                if city not in data["locations"]:
                    data["locations"].append(city)
                    f.seek(0)
                    json.dump(data, f)
                    f.truncate()
        except Exception as e:
            print(f"Error saving location: {e}")

    @staticmethod
    def log_weather(city: str, weather_data: dict):
        """Log weather data with improved error handling"""
        try:
            DataHandler.init_files()
            new_entry = {
                "city": city,
                "temp": weather_data["main"]["temp"],
                "humidity": weather_data["main"]["humidity"],
                "conditions": weather_data["weather"][0]["main"],
                "pressure": weather_data["main"]["pressure"],
                "wind_speed": weather_data["wind"]["speed"],
                "visibility": weather_data.get("visibility", 0)/1000,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                df = pd.read_csv(WEATHER_HISTORY)
            except:
                df = pd.DataFrame()
                
            df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
            df.to_csv(WEATHER_HISTORY, index=False)
        except Exception as e:
            print(f"Error logging weather: {e}")

    @staticmethod
    def get_saved_locations() -> list:
        """Get list of favorite locations with error handling"""
        try:
            DataHandler.init_files()
            with open(SAVED_LOCATIONS, 'r', encoding='utf-8') as f:
                return json.load(f).get("locations", [])
        except:
            return []

    @staticmethod
    def export_to_excel() -> Path:
        """Simplified Excel export without formatting"""
        try:
            DataHandler.init_files()
            df = pd.read_csv(WEATHER_HISTORY)
            excel_path = BACKUP_DIR / f"weather_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            df.to_excel(excel_path, index=False)
            return excel_path
        except Exception as e:
            print(f"Excel export error: {e}")
            return None

    @staticmethod
    def create_backup() -> Path:
        """Create ZIP backup with error handling"""
        try:
            DataHandler.init_files()
            backup_path = BACKUP_DIR / f"weather_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            with ZipFile(backup_path, 'w') as zipf:
                for file in [SAVED_LOCATIONS, WEATHER_HISTORY]:
                    if file.exists():
                        zipf.write(file, arcname=file.name)
            return backup_path
        except Exception as e:
            print(f"Backup error: {e}")
            return None

    @staticmethod
    def get_weather_history(city: str = None, days: int = 30) -> pd.DataFrame:
        """Get historical weather data with improved error handling"""
        try:
            DataHandler.init_files()
            df = pd.read_csv(WEATHER_HISTORY)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            if city:
                df = df[df['city'] == city]
            
            cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
            return df[df['timestamp'] >= cutoff_date].sort_values('timestamp')
        except:
            return pd.DataFrame()

    @staticmethod
    def clear_history(days: int = 30) -> int:
        """Clear old historical data with error handling"""
        try:
            df = DataHandler.get_weather_history(days=days)
            df.to_csv(WEATHER_HISTORY, index=False)
            return len(df)
        except:
            return 0