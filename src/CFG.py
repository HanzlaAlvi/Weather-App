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
