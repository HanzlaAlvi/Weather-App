import pytest
from src.gui import WeatherApp
import tkinter as tk

@pytest.fixture
def app():
    root = tk.Tk()
    app = WeatherApp()
    yield app
    root.destroy()

# 1. Valid Normal Conditions
def test_valid_normal_conditions(app):
    """Valid temp (15°C), valid wind (5 m/s), valid condition (Clear)"""
    test_data = {
        'main': {'temp': 15, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert len(app.alerts) == 0  # No alerts expected

# 2. Valid Alert Conditions
def test_valid_alert_conditions(app):
    """Valid high temp (36°C), valid high wind (11 m/s), valid alert condition (Thunderstorm)"""
    test_data = {
        'main': {'temp': 36},
        'weather': [{'main': 'Thunderstorm'}],
        'wind': {'speed': 11},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert len(app.alerts) == 3  # Expect all three alerts

# 3. Invalid Temperature (Should Fail)
def test_invalid_temperature(app):
    """Invalid temp (missing), valid wind (8 m/s), valid condition (Clouds)"""
    test_data = {
        'main': {'humidity': 50},  # Missing temp
        'weather': [{'main': 'Clouds'}],
        'wind': {'speed': 8},
        'sys': {}
    }
    with pytest.raises(KeyError):
        app.check_weather_alerts(test_data)  # Should fail

# 4. Invalid Wind Speed (Should Fail)
def test_invalid_wind_speed(app):
    """Valid temp (20°C), invalid wind (-5 m/s), valid condition (Clear)"""
    test_data = {
        'main': {'temp': 20},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': -5},  # Invalid negative
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert test_data['wind']['speed'] >= 0  # This assertion will fail

# 5. Invalid Weather Condition (Should Fail)
def test_invalid_weather_condition(app):
    """Valid temp (25°C), valid wind (3 m/s), invalid condition (empty array)"""
    test_data = {
        'main': {'temp': 25},
        'weather': [],  # Invalid empty
        'wind': {'speed': 3},
        'sys': {}
    }
    with pytest.raises(IndexError):
        app.check_weather_alerts(test_data)  # Should fail