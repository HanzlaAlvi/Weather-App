import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
from PIL import Image, ImageTk, ImageOps
import io
import requests
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from src.weather_api import WeatherAPI
from src.data_handler import DataHandler
from config import ICON_DIR, BG_DIR
import os
from plyer import notification
from gtts import gTTS
import pygame
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import pandas as pd

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
        """Configure modern UI styles"""
        # Color schemes
        self.light_bg = "#f5f7fa"
        self.light_fg = "#2c3e50"
        self.light_card = "#ffffff"
        self.dark_bg = "#1a1a2e"
        self.dark_fg = "#e6e6e6"
        self.dark_card = "#16213e"
        self.accent = "#3498db"
        self.warning = "#e74c3c"
        
        # Main styles
        self.style.configure('.', font=('Segoe UI', 10))
        self.style.configure('TFrame', background=self.light_bg)
        self.style.configure('TLabel', background=self.light_bg, foreground=self.light_fg)
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), 
                           foreground=self.accent)
        self.style.configure('Temp.TLabel', font=('Segoe UI', 72), foreground=self.accent)
        self.style.configure('Card.TFrame', background=self.light_card, 
                           borderwidth=2, relief='groove', padding=15)
        self.style.configure('Card.TLabel', background=self.light_card)
        
        # Button styles
        self.style.configure('TButton', padding=8, relief='flat')
        self.style.map('TButton',
            foreground=[('pressed', 'white'), ('active', 'white')],
            background=[('pressed', '#2980b9'), ('active', self.accent)],
            relief=[('pressed', 'sunken'), ('!pressed', 'flat')]
        )
        
        # Warning button style
        self.style.configure('Warning.TButton', foreground='white', background=self.warning)
        
        # Entry style
        self.style.configure('TEntry', fieldbackground='white', padding=8)
        
    def create_widgets(self):
        """Create all modern UI components"""
        # Main container with gradient background
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with app title and controls
        self.create_header()
        
        # Search panel
        self.create_search_panel()
        
        # Current weather display
        self.create_current_weather_panel()
        
        # Weather details
        self.create_details_panel()
        
        # Forecast section
        self.create_forecast_panel()
        
        # Additional features panel
        self.create_features_panel()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Modern app header"""
        self.header = ttk.Frame(self.main_frame)
        self.header.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        # App title with icon
        self.title_frame = ttk.Frame(self.header)
        ttk.Label(self.title_frame, text="🌤 WeatherVision", 
                 style='Header.TLabel').pack(side=tk.LEFT)
        self.title_frame.pack(side=tk.LEFT)
        
        # Control buttons
        self.controls_frame = ttk.Frame(self.header)
        
        # Voice forecast button
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
        """Modern search panel"""
        self.search_frame = ttk.Frame(self.main_frame)
        self.search_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # Search entry with placeholder
        self.city_entry = ttk.Entry(self.search_frame, font=('Segoe UI', 12))
        self.city_entry.insert(0, "Enter city name...")
        self.city_entry.bind('<FocusIn>', self.clear_placeholder)
        self.city_entry.bind('<FocusOut>', self.restore_placeholder)
        self.city_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        # Search button with icon
        self.search_btn = ttk.Button(self.search_frame, text="🔍 Search", 
                                    command=self.update_weather)
        self.search_btn.pack(side=tk.LEFT)
        
        # Bind Enter key
        self.city_entry.bind('<Return>', lambda e: self.update_weather())
    
    def create_current_weather_panel(self):
        """Card-style current weather display"""
        self.current_weather_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.current_weather_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 20), expand=True)
        
        # Top row - icon and temp
        self.top_row = ttk.Frame(self.current_weather_frame)
        self.top_row.pack(fill=tk.X, pady=(0, 20))
        
        # Weather icon
        self.weather_icon = ttk.Label(self.top_row)
        self.weather_icon.pack(side=tk.LEFT, padx=20)
        
        # Temperature and city
        self.temp_frame = ttk.Frame(self.top_row)
        self.temp_label = ttk.Label(self.temp_frame, style='Temp.TLabel', text="--°C")
        self.temp_label.pack(anchor='w')
        
        self.city_label = ttk.Label(self.temp_frame, text="", font=('Segoe UI', 14))
        self.city_label.pack(anchor='w')
        
        self.temp_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Time and date
        self.time_label = ttk.Label(self.top_row, text="", font=('Segoe UI', 12))
        self.time_label.pack(side=tk.RIGHT, padx=20)
    
    def create_details_panel(self):
        """Detailed weather information"""
        self.details_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        self.details_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 20))
        
        # Create a grid of details
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
            
            # Store variables for updates
            setattr(self, f"{label.lower()}_var", var)
            
            # Make cells expand evenly
            self.details_frame.columnconfigure(i%3, weight=1)
            self.details_frame.rowconfigure(i//3, weight=1)
    
    def create_forecast_panel(self):
        """Interactive forecast section"""
        self.forecast_frame = ttk.Frame(self.main_frame)
        self.forecast_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 20), expand=True)
        
        ttk.Label(self.forecast_frame, text="5-Day Forecast", 
                 style='Header.TLabel').pack(anchor='w', pady=(0, 10))
        
        # Canvas for horizontal scrolling
        self.forecast_canvas = tk.Canvas(self.forecast_frame, 
                                        highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.forecast_frame, 
                                      orient='horizontal', 
                                      command=self.forecast_canvas.xview)
        
        self.forecast_canvas.configure(xscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(fill=tk.X)
        self.forecast_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Container frame inside canvas
        self.forecast_container = ttk.Frame(self.forecast_canvas)
        self.forecast_canvas.create_window((0,0), window=self.forecast_container, 
                                          anchor='nw', tags='forecast_frame')
        
        # Bind canvas resize
        self.forecast_container.bind('<Configure>', 
                                   lambda e: self.forecast_canvas.configure(
                                       scrollregion=self.forecast_canvas.bbox('all')))
    
    def create_features_panel(self):
        """Additional features panel"""
        self.features_frame = ttk.Frame(self.main_frame)
        self.features_frame.pack(fill=tk.BOTH, padx=20, pady=(0, 20))
        
        # Feature buttons
        features = [
            ("📈 View Graph", self.show_graph),
            ("📧 Email Report", self.email_report),
            ("📁 Backup Data", DataHandler.create_backup),
            ("🗺️ Show Map", self.show_map)
        ]
        
        for text, command in features:
            btn = ttk.Button(self.features_frame, text=text, command=command)
            btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
    
    def create_status_bar(self):
        """Modern status bar"""
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Frame(self.main_frame)
        self.status_bar.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        ttk.Label(self.status_bar, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Update time
        self.time_var = tk.StringVar()
        ttk.Label(self.status_bar, textvariable=self.time_var).pack(side=tk.RIGHT)
        self.update_clock()
    
    def update_clock(self):
        """Update time in status bar"""
        now = datetime.now().strftime("%H:%M:%S | %d %b %Y")
        self.time_var.set(now)
        self.after(1000, self.update_clock)
    
    def clear_placeholder(self, event):
        """Clear placeholder text"""
        if self.city_entry.get() == "Enter city name...":
            self.city_entry.delete(0, tk.END)
            self.city_entry.configure(foreground='black')
    
    def restore_placeholder(self, event):
        """Restore placeholder if empty"""
        if not self.city_entry.get():
            self.city_entry.insert(0, "Enter city name...")
            self.city_entry.configure(foreground='gray')
    
    def update_weather(self, city=None):
        """Fetch and display weather data"""
        city = city or self.city_entry.get().strip()
        if not city or city == "Enter city name...":
            messagebox.showerror("Error", "Please enter a city name")
            return
            
        try:
            self.status_var.set(f"🌍 Fetching weather for {city}...")
            self.update_idletasks()
            
            # Get current weather
            current_data = WeatherAPI.get_weather(city, self.current_unit)
            
            if current_data.get("cod") != 200:
                messagebox.showerror("Error", current_data.get("message", "Unknown error"))
                return
                
            self.current_city = city
            self.current_data = current_data
            self.display_weather(current_data)
            DataHandler.save_location(city)
            DataHandler.log_weather(city, current_data)
            
            # Get forecast
            self.update_forecast()
            
            # Check for alerts
            self.check_weather_alerts(current_data)
            
            self.status_var.set(f"✅ Weather data loaded for {city}")
            
            # Update last update time
            self.last_update = datetime.now().strftime("%H:%M:%S")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch weather: {str(e)}")
            self.status_var.set("❌ Error fetching weather data")
    
    def display_weather(self, data):
        """Update UI with weather data"""
        # City and time
        self.city_label.config(text=f"{data['name']}, {data['sys']['country']}")
        self.time_label.config(text=datetime.now().strftime("%H:%M | %a %d %b"))
        
        # Temperature
        unit = "°C" if self.current_unit == "metric" else "°F"
        self.temp_label.config(text=f"{data['main']['temp']:.1f}{unit}")
        
        # Weather icon
        icon_code = data['weather'][0]['icon']
        self.update_weather_icon(icon_code)
        
        # Details
        self.humidity_var.set(f"{data['main']['humidity']}%")
        self.wind_var.set(f"{data['wind']['speed']} m/s")
        self.pressure_var.set(f"{data['main']['pressure']} hPa")
        self.visibility_var.set(f"{data.get('visibility', 0)/1000:.1f} km")
        
        # Sunrise/sunset
        sunrise = datetime.fromtimestamp(data['sys']['sunrise']).strftime("%H:%M")
        sunset = datetime.fromtimestamp(data['sys']['sunset']).strftime("%H:%M")
        self.sunrise_var.set(sunrise)
        self.sunset_var.set(sunset)
    
    def update_weather_icon(self, icon_code):
        """Load and display weather icon with animation effect"""
        icon_path = ICON_DIR / f"{icon_code}.png"
        
        try:
            if icon_path.exists():
                img = Image.open(icon_path)
            else:
                # Download icon if not exists
                icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"
                response = requests.get(icon_url, stream=True)
                img = Image.open(io.BytesIO(response.content))
                img.save(icon_path)
            
            # Apply theme filter
            if self.theme_mode == "dark":
                img = ImageOps.invert(img.convert('RGB'))
            
            # Smooth resize animation
            for size in range(50, 151, 10):
                resized = img.resize((size, size), Image.LANCZOS)
                self.weather_photo = ImageTk.PhotoImage(resized)
                self.weather_icon.config(image=self.weather_photo)
                self.update_idletasks()
                time.sleep(0.02)
                
        except Exception as e:
            print(f"Error loading icon: {e}")
    
    def update_forecast(self):
        """Display 5-day forecast with smooth transitions"""
        try:
            forecast = WeatherAPI.get_forecast(self.current_city, units=self.current_unit)
            
            # Clear previous forecast
            for widget in self.forecast_container.winfo_children():
                widget.destroy()
            
            # Create forecast cards
            for i in range(0, len(forecast['list']), 8):  # Daily forecast (every 24h)
                day_data = forecast['list'][i]
                day_frame = ttk.Frame(self.forecast_container, style='Card.TFrame')
                day_frame.pack(side=tk.LEFT, padx=10, pady=5, ipadx=10, ipady=10)
                
                # Date
                date = datetime.strptime(day_data['dt_txt'], "%Y-%m-%d %H:%M:%S")
                ttk.Label(day_frame, 
                         text=date.strftime("%a\n%d %b"), 
                         font=('Segoe UI', 10, 'bold')).pack()
                
                # Icon
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
                
                # Temp
                temp = day_data['main']['temp']
                unit = "°C" if self.current_unit == "metric" else "°F"
                ttk.Label(day_frame, 
                         text=f"{temp:.1f}{unit}", 
                         font=('Segoe UI', 12, 'bold')).pack()
                
                # Conditions
                ttk.Label(day_frame, 
                         text=day_data['weather'][0]['description'].title(),
                         font=('Segoe UI', 9)).pack()
            
            # Update canvas scroll region
            self.forecast_container.update_idletasks()
            self.forecast_canvas.config(scrollregion=self.forecast_canvas.bbox('all'))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load forecast: {str(e)}")
    
    def check_weather_alerts(self, data):
        """Check for weather alerts and notify user"""
        self.alerts = []
        
        # Temperature alerts
        temp = data['main']['temp']
        if temp > 35:  # Very hot
            self.alerts.append(f"High temperature warning: {temp}°C")
        elif temp < 5:  # Very cold
            self.alerts.append(f"Low temperature warning: {temp}°C")
        
        # Weather condition alerts
        condition = data['weather'][0]['main']
        if condition in ['Thunderstorm', 'Extreme']:
            self.alerts.append(f"Weather alert: {condition}")
        
        # Wind alerts
        wind_speed = data['wind']['speed']
        if wind_speed > 10:  # 10 m/s ~ 36 km/h
            self.alerts.append(f"High wind warning: {wind_speed} m/s")
        
        # Update alerts button
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
        """Display weather alerts"""
        if self.alerts:
            alert_text = "\n\n• ".join([""] + self.alerts)
            messagebox.showwarning("Weather Alerts", alert_text)
        else:
            messagebox.showinfo("Weather Alerts", "No active weather alerts")
    
    def speak_weather(self):
        """Convert weather to speech"""
        if not hasattr(self, 'current_data'):
            return
            
        data = self.current_data
        text = f"Current weather in {data['name']}: {data['weather'][0]['description']}. "
        text += f"Temperature {data['main']['temp']} degrees. "
        text += f"Humidity {data['main']['humidity']} percent. "
        text += f"Wind speed {data['wind']['speed']} meters per second."
        
        try:
            # Generate speech
            tts = gTTS(text=text, lang='en')
            tts.save("weather_report.mp3")
            
            # Play audio
            pygame.mixer.music.load("weather_report.mp3")
            pygame.mixer.music.play()
            
        except Exception as e:
            messagebox.showerror("Voice Error", f"Failed to generate speech: {str(e)}")
    
    def show_graph(self):
        """Display temperature graph"""
        try:
            history = DataHandler.get_weather_history(self.current_city)
            if history.empty:
                messagebox.showinfo("Info", "No historical data available")
                return
            
            # Create figure
            fig, ax = plt.subplots(figsize=(8, 4))
            history['timestamp'] = pd.to_datetime(history['timestamp'])
            history.plot(x='timestamp', y='temp', ax=ax, legend=False)
            
            ax.set_title(f"Temperature Trend for {self.current_city}")
            ax.set_ylabel("Temperature (°C)")
            ax.grid(True)
            
            # Embed in Tkinter
            graph_window = tk.Toplevel(self)
            graph_window.title("Temperature Graph")
            
            canvas = FigureCanvasTkAgg(fig, master=graph_window)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate graph: {str(e)}")
    
    def email_report(self):
        """Send weather report via email"""
        if not hasattr(self, 'current_data'):
            messagebox.showerror("Error", "No weather data to send")
            return
            
        try:
            # Create email content
            data = self.current_data
            msg = MIMEMultipart()
            msg['Subject'] = f"Weather Report for {data['name']}"
            msg['From'] = "weather_app@example.com"
            
            # Get recipient from user
            recipient = simpledialog.askstring("Email", "Enter recipient email:")
            if not recipient:
                return
                
            msg['To'] = recipient
            
            # HTML email body
            html = f"""
            <h1>Weather Report for {data['name']}, {data['sys']['country']}</h1>
            <p><strong>Conditions:</strong> {data['weather'][0]['description']}</p>
            <p><strong>Temperature:</strong> {data['main']['temp']}°C</p>
            <p><strong>Humidity:</strong> {data['main']['humidity']}%</p>
            <p><strong>Wind:</strong> {data['wind']['speed']} m/s</p>
            <p><strong>Report Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            """
            
            msg.attach(MIMEText(html, 'html'))
            
            # Send email (configure your SMTP settings)
            with smtplib.SMTP('localhost') as server:
                server.send_message(msg)
            
            messagebox.showinfo("Success", "Email report sent successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {str(e)}")
    
    def show_map(self):
        """Show weather map (placeholder)"""
        messagebox.showinfo("Map", "Weather map feature coming soon!")
    
    def toggle_units(self):
        """Switch between metric and imperial units"""
        self.current_unit = "imperial" if self.current_unit == "metric" else "metric"
        self.unit_btn.config(text="°F" if self.current_unit == "imperial" else "°C")
        if self.current_city:
            self.update_weather()
    
    def toggle_theme(self):
        """Switch between light and dark theme with smooth transition"""
        self.theme_mode = "dark" if self.theme_mode == "light" else "light"
        self.theme_btn.config(text="☾" if self.theme_mode == "dark" else "☀")
        
        # Define colors
        bg = self.dark_bg if self.theme_mode == "dark" else self.light_bg
        fg = self.dark_fg if self.theme_mode == "dark" else self.light_fg
        card = self.dark_card if self.theme_mode == "dark" else self.light_card
        
        # Smooth transition
        for alpha in [x/10 for x in range(11)]:
            try:
                self.configure(bg=self.blend_colors(
                    self.light_bg if alpha < 1 else bg, 
                    self.dark_bg if alpha < 1 else bg, 
                    alpha
                ))
                self.update_idletasks()
                time.sleep(0.05)
            except:
                pass
        
        # Update all widgets
        self.style.configure('.', 
                           background=bg, 
                           foreground=fg)
        self.style.configure('Card.TFrame', 
                           background=card)
        self.style.configure('Card.TLabel', 
                           background=card)
        
        # Update weather icon
        if hasattr(self, 'current_data'):
            self.update_weather_icon(self.current_data['weather'][0]['icon'])
    
    def blend_colors(self, color1, color2, alpha):
        """Helper for color transitions"""
        # Convert hex to RGB
        def hex_to_rgb(hex):
            return tuple(int(hex[i:i+2], 16) for i in (1, 3, 5))
        
        def rgb_to_hex(rgb):
            return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        blended = tuple(int(rgb1[i] + (rgb2[i] - rgb1[i]) * alpha) for i in range(3))
        return rgb_to_hex(blended)