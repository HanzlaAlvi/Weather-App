#critical path coverage:
import pytest
from src.gui import WeatherApp
import tkinter as tk

@pytest.fixture
def app():
    """Fixture to create and destroy the WeatherApp instance"""
    root = tk.Tk()
    app = WeatherApp()
    yield app
    root.destroy()

def test_critical_path_check_weather_alerts(app):
    """
    Critical Path Test for check_weather_alerts:
    Covers the longest path where all alert conditions are triggered.
    """
    # Critical test input: All conditions should be true
    test_data = {
        'main': {'temp': 38, 'humidity': 50},
        'weather': [{'main': 'Thunderstorm'}],
        'wind': {'speed': 12},
        'sys': {}
    }

    # Run the method with the critical input
    app.check_weather_alerts(test_data)

    # Assertions to verify all critical alerts are present
    assert len(app.alerts) == 3
    assert "High temperature warning" in app.alerts[0]
    assert "Weather alert: Thunderstorm" in app.alerts[1]
    assert "High wind warning" in app.alerts[2]

    # Also verify the alert button turns red
    assert app.alerts_btn.cget("style") == "Warning.TButton"
