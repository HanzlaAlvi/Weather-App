from src.gui import WeatherApp
from src.data_handler import DataHandler

if __name__ == "__main__":
    # Initialize data files
    DataHandler.init_files()
    
    # Create and run application
    app = WeatherApp()
    app.mainloop()