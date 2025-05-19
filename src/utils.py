import json
import pandas as pd
from pathlib import Path
from config import SAVED_LOCATIONS, WEATHER_HISTORY, BACKUP_DIR
import shutil
import os
from datetime import datetime
import openpyxl
from zipfile import ZipFile

class DataHandler:
    @staticmethod
    def init_files():
        """Initialize all required files and directories"""
        WEATHER_HISTORY.parent.mkdir(exist_ok=True)
        BACKUP_DIR.mkdir(exist_ok=True)
        
        if not SAVED_LOCATIONS.exists():
            with open(SAVED_LOCATIONS, 'w') as f:
                json.dump({"locations": []}, f)
        
        if not WEATHER_HISTORY.exists():
            pd.DataFrame(columns=[
                "city", "temp", "humidity", "conditions", "pressure", 
                "wind_speed", "visibility", "timestamp"
            ]).to_csv(WEATHER_HISTORY, index=False)

    @staticmethod
    def save_location(city: str):
        """Save favorite location"""
        DataHandler.init_files()
        with open(SAVED_LOCATIONS, 'r+') as f:
            data = json.load(f)
            if city not in data["locations"]:
                data["locations"].append(city)
                f.seek(0)
                json.dump(data, f)

    @staticmethod
    def log_weather(city: str, weather_data: dict):
        """Log weather data"""
        DataHandler.init_files()
        new_entry = {
            "city": city,
            "temp": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "conditions": weather_data["weather"][0]["main"],
            "pressure": weather_data["main"]["pressure"],
            "wind_speed": weather_data["wind"]["speed"],
            "visibility": weather_data.get("visibility", 0)/1000,  # Convert to km
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            df = pd.read_csv(WEATHER_HISTORY)
        except:
            df = pd.DataFrame()
            
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(WEATHER_HISTORY, index=False)

    @staticmethod
    def get_saved_locations() -> list:
        """Get list of favorite locations"""
        DataHandler.init_files()
        with open(SAVED_LOCATIONS, 'r') as f:
            return json.load(f)["locations"]

    @staticmethod
    def export_to_excel() -> Path:
        """Export weather history to Excel"""
        DataHandler.init_files()
        df = pd.read_csv(WEATHER_HISTORY)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_path = BACKUP_DIR / f"weather_history_{timestamp}.xlsx"
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
            
            workbook = writer.book
            worksheet = writer.sheets['Sheet1']
            
            header_fmt = workbook.add_format({
                'bold': True, 
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#4F81BD',
                'font_color': 'white',
                'border': 1
            })
            
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)
                
            for column in df:
                col_idx = df.columns.get_loc(column)
                worksheet.set_column(col_idx, col_idx, max(
                    df[column].astype(str).map(len).max(),
                    len(column)
                ) + 2)
        
        return excel_path

    @staticmethod
    def create_backup() -> Path:
        """Create ZIP backup of data"""
        DataHandler.init_files()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = BACKUP_DIR / f"weather_backup_{timestamp}.zip"
        
        with ZipFile(backup_path, 'w') as zipf:
            for file in [SAVED_LOCATIONS, WEATHER_HISTORY]:
                zipf.write(file, arcname=file.name)
        
        return backup_path

    @staticmethod
    def get_weather_history(city: str = None, days: int = 30) -> pd.DataFrame:
        """Get historical weather data"""
        DataHandler.init_files()
        df = pd.read_csv(WEATHER_HISTORY)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        if city:
            df = df[df['city'] == city]
        
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        df = df[df['timestamp'] >= cutoff_date]
        
        return df.sort_values('timestamp')

    @staticmethod
    def clear_history(days: int = 30) -> int:
        """Clear old historical data"""
        DataHandler.init_files()
        df = pd.read_csv(WEATHER_HISTORY)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        df = df[df['timestamp'] >= cutoff_date]
        
        df.to_csv(WEATHER_HISTORY, index=False)
        return len(df)