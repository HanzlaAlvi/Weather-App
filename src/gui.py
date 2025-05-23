import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk, ImageOps
import io
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.weather_api import WeatherAPI
from src.data_handler import DataHandler
from config import ICON_DIR, BG_DIR, EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASSWORD
import os
from plyer import notification
from gtts import gTTS
import pygame
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import pandas as pd
from pathlib import Path

class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("WeatherVision Pro+")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # Initialize pygame for sound
        pygame.mixer.init()
        
        # Style Configuration
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.current_unit = "metric"
        self.theme_mode = "light"
        self.current_city = ""
        self.alerts = []
        self.current_data = None
        
        # Configure custom styles
        self.configure_styles()
        
        # Initialize UI
        self.create_widgets()
        DataHandler.init_files()
        
        # Start with default city
        self.after(1000, lambda: self.update_weather("Delhi"))
        
    def configure_styles(self):
        """Configure modern UI styles for both light and dark modes"""
        # Color schemes
        self.light_bg = "#f5f7fa"
        self.light_fg = "#2c3e50"
        self.light_card = "#ffffff"
        self.dark_bg = "#1a1a2e"
        self.dark_fg = "#e6e6e6"
        self.dark_card = "#16213e"
        self.accent = "#3498db"
        self.warning = "#e74c3c"

        # Base styles
        self.style.configure('.', 
                           font=('Segoe UI', 10),
                           background=self.light_bg,
                           foreground=self.light_fg)
        
        # Frame styles
        self.style.configure('TFrame', background=self.light_bg)
        
        # Label styles
        self.style.configure('TLabel', 
                           background=self.light_bg, 
                           foreground=self.light_fg)
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 18, 'bold'), 
                           foreground=self.accent)
        self.style.configure('Temp.TLabel', 
                           font=('Segoe UI', 72), 
                           foreground=self.accent)
        
        # Card styles
        self.style.configure('Card.TFrame', 
                           background=self.light_card, 
                           borderwidth=2, 
                           relief='groove', 
                           padding=15)
        self.style.configure('Card.TLabel', 
                           background=self.light_card,
                           foreground=self.light_fg)
        
        # Button styles
        self.style.configure('TButton', 
                           padding=8, 
                           relief='flat',
                           background=self.accent,
                           foreground='white')
        self.style.map('TButton',
            foreground=[('pressed', 'white'), ('active', 'white')],
            background=[('pressed', '#2980b9'), ('active', self.accent)],
            relief=[('pressed', 'sunken'), ('!pressed', 'flat')]
        )
        
        # Warning button style
        self.style.configure('Warning.TButton', 
                           foreground='white', 
                           background=self.warning)
        
        # Entry style
        self.style.configure('TEntry', 
                           fieldbackground='white', 
                           padding=8,
                           foreground='black')
        
        # Treeview styles
        self.style.configure('Treeview', 
                           background=self.light_card,
                           foreground=self.light_fg,
                           rowheight=25,
                           fieldbackground=self.light_card)
        self.style.configure('Treeview.Heading', 
                           background=self.accent,
                           foreground='white',
                           padding=5,
                           font=('Segoe UI', 10, 'bold'))
        self.style.map('Treeview',
            background=[('selected', '#2980b9')],
            foreground=[('selected', 'white')])
        
    def create_widgets(self):
        """Create all UI components with improved layout"""
        # Main container with grid layout
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configure grid weights
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)  # Give more space to current weather
        
        # Header - Row 0
        self.create_header()
        self.header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Search panel - Row 1
        self.create_search_panel()
        self.search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Current weather - Row 2
        self.create_current_weather_panel()
        self.current_weather_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        
        # 5-Day Forecast - Row 3
        self.create_forecast_panel()
        self.forecast_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        
        # Weather details - Row 4
        self.create_details_panel()
        self.details_frame.grid(row=4, column=0, sticky="ew", pady=(0, 10))
        
        # Features panel - Row 5 (centered at bottom)
        self.create_features_panel()
        self.features_frame.grid(row=5, column=0, sticky="", pady=(10, 0))
        
        # Status bar - Row 6
        self.create_status_bar()
        self.status_bar.grid(row=6, column=0, sticky="ew", pady=(10, 0))
    
    def create_header(self):
        """App header with controls"""
        self.header = ttk.Frame(self.main_frame)
        
        # App title
        self.title_frame = ttk.Frame(self.header)
        ttk.Label(self.title_frame, text="🌤 WeatherVision", 
                 style='Header.TLabel').pack(side=tk.LEFT)
        self.title_frame.pack(side=tk.LEFT)
        
        # Control buttons
        self.controls_frame = ttk.Frame(self.header)
        
        # Voice button
        self.voice_btn = ttk.Button(self.controls_frame, text="🔊", 
                                  command=self.speak_weather, width=3)
        self.voice_btn.pack(side=tk.LEFT, padx=5)
        
        # Theme toggle
        self.theme_btn = ttk.Button(self.controls_frame, text="☀", 
                                  command=self.toggle_theme, width=3)
        self.theme_btn.pack(side=tk.LEFT, padx=5)
        
        # Unit toggle
        self.unit_btn = ttk.Button(self.controls_frame, text="°C/°F", 
                                 command=self.toggle_units)
        self.unit_btn.pack(side=tk.LEFT, padx=5)
        
        # Alerts button
        self.alerts_btn = ttk.Button(self.controls_frame, text="⚠", 
                                   command=self.show_alerts, width=3)
        self.alerts_btn.pack(side=tk.LEFT, padx=5)
        
        self.controls_frame.pack(side=tk.RIGHT)
    
    def create_search_panel(self):
        """City search panel"""
        self.search_frame = ttk.Frame(self.main_frame)
        
        # Search entry
        self.city_entry = ttk.Entry(self.search_frame, font=('Segoe UI', 12))
        self.city_entry.insert(0, "Enter city name...")
        self.city_entry.bind('<FocusIn>', self.clear_placeholder)
        self.city_entry.bind('<FocusOut>', self.restore_placeholder)
        self.city_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        # Search button
        self.search_btn = ttk.Button(self.search_frame, text="🔍 Search", 
                                    command=self.update_weather)
        self.search_btn.pack(side=tk.LEFT)
        
        self.city_entry.bind('<Return>', lambda e: self.update_weather())
    
    def create_forecast_panel(self):
        """5-Day Forecast - horizontal scrollable"""
        self.forecast_frame = ttk.Frame(self.main_frame)
        
        ttk.Label(self.forecast_frame, text="5-Day Forecast", 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 5))
        
        # Container for forecast cards
        self.forecast_container = ttk.Frame(self.forecast_frame)
        self.forecast_container.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas and horizontal scrollbar
        self.forecast_canvas = tk.Canvas(self.forecast_container, height=150, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.forecast_container, 
                                      orient='horizontal', 
                                      command=self.forecast_canvas.xview)
        
        self.forecast_canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.forecast_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for forecast items
        self.forecast_inner = ttk.Frame(self.forecast_canvas)
        self.forecast_canvas.create_window((0,0), window=self.forecast_inner, anchor='nw')
        
        # Configure canvas scrolling
        self.forecast_inner.bind('<Configure>', 
                               lambda e: self.forecast_canvas.configure(
                                   scrollregion=self.forecast_canvas.bbox('all')))
    
    def create_current_weather_panel(self):
        """Current weather display - more compact layout"""
        self.current_weather_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        # Weather icon and temp - top row
        self.top_row = ttk.Frame(self.current_weather_frame)
        self.top_row.pack(fill=tk.X, pady=10)
        
        # Weather icon left
        self.weather_icon = ttk.Label(self.top_row)
        self.weather_icon.pack(side=tk.LEFT, padx=20)
        
        # Temperature and city in center
        self.temp_frame = ttk.Frame(self.top_row)
        self.temp_label = ttk.Label(self.temp_frame, style='Temp.TLabel', text="--°C")
        self.temp_label.pack(anchor='center')
        
        self.city_label = ttk.Label(self.temp_frame, text="", font=('Segoe UI', 14))
        self.city_label.pack(anchor='center')
        self.temp_frame.pack(side=tk.LEFT, expand=True)
        
        # Time on right
        self.time_label = ttk.Label(self.top_row, text="", font=('Segoe UI', 12))
        self.time_label.pack(side=tk.RIGHT, padx=20)
    
    def create_details_panel(self):
        """Weather details panel"""
        self.details_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        details = [
            ("Humidity", "--%", "💧"),
            ("Wind", "-- m/s", "🌬️"), 
            ("Pressure", "-- hPa", "📊"),
            ("Visibility", "-- km", "👁️"),
            ("Sunrise", "--:--", "🌅"),
            ("Sunset", "--:--", "🌇")
        ]
        
        for i, (label, value, icon) in enumerate(details):
            frame = ttk.Frame(self.details_frame)
            frame.grid(row=i//3, column=i%3, padx=10, pady=10, sticky='nsew')
            
            ttk.Label(frame, text=f"{icon} {label}", font=('Segoe UI', 10)).pack()
            var = tk.StringVar(value=value)
            ttk.Label(frame, textvariable=var, font=('Segoe UI', 12, 'bold')).pack()
            
            setattr(self, f"{label.lower()}_var", var)
            self.details_frame.columnconfigure(i%3, weight=1)
            self.details_frame.rowconfigure(i//3, weight=1)
    
    def create_features_panel(self):
        """Features panel at BOTTOM with email - centered"""
        self.features_frame = ttk.Frame(self.main_frame)
        
        features = [
            ("📈 View Graph", self.show_graph),
            ("🗺️ Show Map", self.show_map),
            ("📁 Backup Data", self.show_backup_data),
            ("📧 Email Report", self.email_report)
        ]
        
        for i, (text, command) in enumerate(features):
            btn = ttk.Button(self.features_frame, 
                           text=text, 
                           command=command,
                           width=15)
            btn.grid(row=0, column=i, padx=5, pady=5)
        
        # Center the buttons in the frame
        self.features_frame.columnconfigure(len(features), weight=1)
    
    def create_status_bar(self):
        """Status bar at bottom"""
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Frame(self.main_frame)
        
        ttk.Label(self.status_bar, textvariable=self.status_var).pack(side=tk.LEFT)
        self.time_var = tk.StringVar()
        ttk.Label(self.status_bar, textvariable=self.time_var).pack(side=tk.RIGHT)
        self.update_clock()
    
    def update_clock(self):
        """Update time in status bar"""
        now = datetime.now().strftime("%H:%M:%S | %d %b %Y")
        self.time_var.set(now)
        self.after(1000, self.update_clock)
    
    def clear_placeholder(self, event):
        if self.city_entry.get() == "Enter city name...":
            self.city_entry.delete(0, tk.END)
            self.city_entry.configure(foreground='black')
    
    def restore_placeholder(self, event):
        if not self.city_entry.get():
            self.city_entry.insert(0, "Enter city name...")
            self.city_entry.configure(foreground='gray')
    
    def update_weather(self, city=None):
        city = city or self.city_entry.get().strip()
        if not city or city == "Enter city name...":
            messagebox.showerror("Error", "Please enter a city name")
            return
            
        try:
            self.status_var.set(f"🌍 Fetching weather for {city}...")
            self.update_idletasks()
            
            current_data = WeatherAPI.get_weather(city, self.current_unit)
            
            if current_data.get("cod") != 200:
                messagebox.showerror("Error", current_data.get("message", "Unknown error"))
                return
                
            self.current_city = city
            self.current_data = current_data
            self.display_weather(current_data)
            DataHandler.save_location(city)
            DataHandler.log_weather(city, current_data)
            
            self.update_forecast()
            self.check_weather_alerts(current_data)
            
            self.status_var.set(f"✅ Weather data loaded for {city}")
            self.last_update = datetime.now().strftime("%H:%M:%S")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch weather: {str(e)}")
            self.status_var.set("❌ Error fetching weather data")
    
    def display_weather(self, data):
        self.city_label.config(text=f"{data['name']}, {data['sys']['country']}")
        self.time_label.config(text=datetime.now().strftime("%H:%M | %a %d %b"))
        
        unit = "°C" if self.current_unit == "metric" else "°F"
        self.temp_label.config(text=f"{data['main']['temp']:.1f}{unit}")
        
        icon_code = data['weather'][0]['icon']
        self.update_weather_icon(icon_code)
        
        self.humidity_var.set(f"{data['main']['humidity']}%")
        self.wind_var.set(f"{data['wind']['speed']} m/s")
        self.pressure_var.set(f"{data['main']['pressure']} hPa")
        self.visibility_var.set(f"{data.get('visibility', 0)/1000:.1f} km")
        
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M")
        self.sunrise_var.set(sunrise)
        self.sunset_var.set(sunset)
    
    def update_weather_icon(self, icon_code):
        icon_path = ICON_DIR / f"{icon_code}.png"
        
        try:
            if icon_path.exists():
                img = Image.open(icon_path)
            else:
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
                response = requests.get(icon_url, stream=True)
                img = Image.open(io.BytesIO(response.content))
                img.save(icon_path)
            
            if self.theme_mode == "dark":
                img = ImageOps.invert(img.convert('RGB'))
            
            for size in range(50, 151, 10):
                resized = img.resize((size, size), Image.LANCZOS)
                self.weather_photo = ImageTk.PhotoImage(resized)
                self.weather_icon.config(image=self.weather_photo)
                self.update_idletasks()
                time.sleep(0.02)
                
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    def update_forecast(self):
        try:
            forecast = WeatherAPI.get_forecast(self.current_city, units=self.current_unit)
            
            for widget in self.forecast_inner.winfo_children():
                widget.destroy()
            
            for i in range(0, len(forecast['list']), 8):
                day_data = forecast['list'][i]
                day_frame = ttk.Frame(self.forecast_inner, style='Card.TFrame')
                day_frame.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=10)
                
                date = datetime.strptime(day_data['dt_txt'], "%Y-%m-%d %H:%M:%S")
                ttk.Label(day_frame, 
                         text=date.strftime("%a\n%d %b"), 
                         font=('Segoe UI', 10, 'bold')).pack()
                
                icon_code = day_data['weather'][0]['icon']
                icon_path = ICON_DIR / f"{icon_code}.png"
                if icon_path.exists():
                    img = Image.open(icon_path)
                    img = img.resize((60, 60), Image.LANCZOS)
                    if self.theme_mode == "dark":
                        img = ImageOps.invert(img.convert('RGB'))
                    icon = ImageTk.PhotoImage(img)
                    icon_label = ttk.Label(day_frame, image=icon)
                    icon_label.image = icon
                    icon_label.pack()
                
                temp = day_data['main']['temp']
                unit = "°C" if self.current_unit == "metric" else "°F"
                ttk.Label(day_frame, 
                         text=f"{temp:.1f}{unit}", 
                         font=('Segoe UI', 12, 'bold')).pack()
                
                ttk.Label(day_frame, 
                         text=day_data['weather'][0]['description'].title(),
                         font=('Segoe UI', 9)).pack()
            
            self.forecast_inner.update_idletasks()
            self.forecast_canvas.config(scrollregion=self.forecast_canvas.bbox('all'))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load forecast: {str(e)}")
    
    def check_weather_alerts(self, data):
        self.alerts = []
        
        temp = data['main']['temp']
        if temp > 35:
            self.alerts.append(f"High temperature warning: {temp}°C")
        elif temp < 5:
            self.alerts.append(f"Low temperature warning: {temp}°C")
        
        condition = data['weather'][0]['main']
        if condition in ['Thunderstorm', 'Extreme']:
            self.alerts.append(f"Weather alert: {condition}")
        
        wind_speed = data['wind']['speed']
        if wind_speed > 10:
            self.alerts.append(f"High wind warning: {wind_speed} m/s")
        
        if self.alerts:
            self.alerts_btn.config(style='Warning.TButton')
            notification.notify(
                title="Weather Alerts",
                message="\n".join(self.alerts),
                timeout=10
            )
        else:
            self.alerts_btn.config(style='TButton')
    
    def show_alerts(self):
        if self.alerts:
            alert_text = "\n\n• ".join([""] + self.alerts)
            messagebox.showwarning("Weather Alerts", alert_text)
        else:
            messagebox.showinfo("Weather Alerts", "No active weather alerts")
    
    def speak_weather(self):
        if not hasattr(self, 'current_data'):
            messagebox.showerror("Error", "No weather data available")
            return
            
        try:
            data = self.current_data
            text = f"Current weather in {data['name']}: {data['weather'][0]['description']}. "
            text += f"Temperature is {data['main']['temp']} degrees {'Celsius' if self.current_unit == 'metric' else 'Fahrenheit'}. "
            text += f"Humidity is {data['main']['humidity']} percent. "
            text += f"Wind speed is {data['wind']['speed']} meters per second."
            
            tts = gTTS(text=text, lang='en', slow=False)
            
            with io.BytesIO() as f:
                tts.write_to_fp(f)
                f.seek(0)
                pygame.mixer.music.load(f)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
        except Exception as e:
            messagebox.showerror("Voice Error", f"Failed to generate speech: {str(e)}")

    def show_graph(self):
        try:
            history = DataHandler.get_weather_history(self.current_city)
            if history.empty:
                messagebox.showinfo("Info", "No historical data available")
                return
            
            fig, ax = plt.subplots(figsize=(8, 4))
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            history.plot(x='timestamp', y='temp', ax=ax, legend=False)
            
            ax.set_title(f"Temperature Trend for {self.current_city}")
            ax.set_ylabel("Temperature (°C)")
            ax.grid(True)
            
            graph_window = tk.Toplevel(self)
            graph_window.title("Temperature Graph")
            
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate graph: {str(e)}")
    
    def show_backup_data(self):
        """Display backup data in a table format"""
        try:
            history = DataHandler.get_weather_history()
            if history.empty:
                messagebox.showinfo("Info", "No historical data available")
                return
            
            # Create a new window
            backup_window = tk.Toplevel(self)
            backup_window.title("Weather History Data")
            backup_window.geometry("1000x600")
            
            # Center the window
            window_width = 1000
            window_height = 600
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
            x = int((screen_width/2) - (window_width/2))
            y = int((screen_height/2) - (window_height/2))
            backup_window.geometry(f"+{x}+{y}")
            
            # Create a frame for the table
            table_frame = ttk.Frame(backup_window)
            table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Create a treeview widget
            tree = ttk.Treeview(table_frame, show="headings")
            
            # Define columns
            columns = list(history.columns)
            tree["columns"] = columns
            
            # Format columns
            for col in columns:
                tree.heading(col, text=col.title())
                tree.column(col, width=100, anchor='center')
            
            # Add data to the treeview
            for index, row in history.iterrows():
                tree.insert("", tk.END, values=list(row))
            
            # Add scrollbars
            vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
            hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
            
            # Grid layout
            tree.grid(row=0, column=0, sticky="nsew")
            vsb.grid(row=0, column=1, sticky="ns")
            hsb.grid(row=1, column=0, sticky="ew")
            
            # Configure grid weights
            table_frame.rowconfigure(0, weight=1)
            table_frame.columnconfigure(0, weight=1)
            
            # Add export button
            export_btn = ttk.Button(
                backup_window, 
                text="Export to CSV", 
                command=lambda: self.export_data(history)
            )
            export_btn.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load backup data: {str(e)}")
    
    def export_data(self, data):
        """Export data to CSV file"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Save weather data as"
            )
            if file_path:
                data.to_csv(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")
    
    def email_report(self):
        if not hasattr(self, 'current_data'):
            messagebox.showerror("Error", "No weather data to send")
            return
            
        try:
            email_dialog = tk.Toplevel(self)
            email_dialog.title("Email Weather Report")
            email_dialog.geometry("400x300")
            
            # Center dialog
            email_dialog.update_idletasks()
            width = email_dialog.winfo_width()
            height = email_dialog.winfo_height()
            x = (self.winfo_screenwidth() // 2) - (width // 2)
            y = (self.winfo_screenheight() // 2) - (height // 2)
            email_dialog.geometry(f'+{x}+{y}')
            
            # Email content
            ttk.Label(email_dialog, text="Recipient Email:").pack(pady=(0, 5))
            recipient_entry = ttk.Entry(email_dialog, width=40)
            recipient_entry.pack(pady=(0, 15))
            
            ttk.Label(email_dialog, text="Subject:").pack(pady=(0, 5))
            subject_var = tk.StringVar(value=f"Weather Report for {self.current_city}")
            subject_entry = ttk.Entry(email_dialog, textvariable=subject_var, width=40)
            subject_entry.pack(pady=(0, 15))
            
            def send_email():
                recipient = recipient_entry.get().strip()
                subject = subject_entry.get().strip()
                
                if not recipient:
                    messagebox.showerror("Error", "Please enter recipient email")
                    return
                
                try:
                    data = self.current_data
                    msg = MIMEMultipart()
                    msg['Subject'] = subject
                    msg['From'] = EMAIL_USER
                    msg['To'] = recipient
                    
                    html = f"""
                    <h1>Weather Report for {data['name']}, {data['sys']['country']}</h1>
                    <p><strong>Conditions:</strong> {data['weather'][0]['description']}</p>
                    <p><strong>Temperature:</strong> {data['main']['temp']}°{'C' if self.current_unit == 'metric' else 'F'}</p>
                    <p><strong>Feels Like:</strong> {data['main']['feels_like']}°{'C' if self.current_unit == 'metric' else 'F'}</p>
                    <p><strong>Humidity:</strong> {data['main']['humidity']}%</p>
                    <p><strong>Wind Speed:</strong> {data['wind']['speed']} m/s</p>
                    <p><strong>Pressure:</strong> {data['main']['pressure']} hPa</p>
                    <p><strong>Visibility:</strong> {data.get('visibility', 'N/A')} meters</p>
                    <p><strong>Sunrise:</strong> {datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M')}</p>
                    <p><strong>Sunset:</strong> {datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M')}</p>
                    <p><strong>Report Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
                    """
                    
                    msg.attach(MIMEText(html, 'html'))
                    
                    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
                        server.starttls()
                        server.login(EMAIL_USER, EMAIL_PASSWORD)
                        server.send_message(msg)
                    
                    messagebox.showinfo("Success", f"Email sent to {recipient}")
                    email_dialog.destroy()
                    
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to send email: {str(e)}")
            
            send_btn = ttk.Button(email_dialog, text="Send Email", command=send_email)
            send_btn.pack(pady=(10, 0))
            
            recipient_entry.focus_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create email dialog: {str(e)}")
    
    def show_map(self):
        messagebox.showinfo("Map", "Weather map feature coming soon!")
    
    def toggle_units(self):
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"
        self.unit_btn.config(text="°F" if self.current_unit == "imperial" else "°C")
        if self.current_city:
            self.update_weather()
    
    def toggle_theme(self):
        """Complete dark/light mode toggle"""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.theme_btn.config(text="☾" if self.theme_mode == "dark" else "☀")
        
        # Set colors based on theme
        if self.theme_mode == "dark":
            bg = self.dark_bg
            fg = self.dark_fg
            card = self.dark_card
            entry_bg = "#2d2d2d"
            entry_fg = "white"
        else:
            bg = self.light_bg
            fg = self.light_fg
            card = self.light_card
            entry_bg = "white"
            entry_fg = "black"
        
        # Apply theme to all components
        self.configure(background=bg)
        
        # Update all styles
        self.style.configure('.', background=bg, foreground=fg)
        self.style.configure('TFrame', background=bg)
        self.style.configure('TLabel', background=bg, foreground=fg)
        self.style.configure('Card.TFrame', background=card)
        self.style.configure('Card.TLabel', background=card, foreground=fg)
        self.style.configure('TEntry', 
                           fieldbackground=entry_bg, 
                           foreground=entry_fg)
        self.style.configure('Treeview', 
                           background=card,
                           foreground=fg,
                           fieldbackground=card)
        
        # Update entry field colors
        self.city_entry.configure(foreground=entry_fg)
        if self.city_entry.get() == "Enter city name...":
            self.city_entry.configure(foreground='gray' if self.theme_mode == 'light' else '#aaaaaa')
        
        # Update weather icon if data exists
        if hasattr(self, 'current_data'):
            self.update_weather_icon(self.current_data['weather'][0]['icon'])
    
    def blend_colors(self, color1, color2, alpha):
        """Helper for color transitions"""
        def hex_to_rgb(hex):
            return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))
        
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        blended = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * alpha) for i in range(3))
        return rgb_to_hex(blended)