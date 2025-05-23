import pytest
from src.gui import WeatherApp
from unittest.mock import MagicMock
import tkinter as tk

@pytest.fixture
def app():
    root = tk.Tk()
    app = WeatherApp()
    yield app
    root.destroy()

def test_no_alerts_for_normal_conditions(app):
    """Test no alerts are generated for normal weather conditions"""
    test_data = {
        'main': {'temp': 20, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert len(app.alerts) == 0

def test_high_temperature_alert(app):
    """Test alert for high temperature (>35°C)"""
    test_data = {
        'main': {'temp': 36, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert "High temperature warning" in app.alerts[0]

def test_low_temperature_alert(app):
    """Test alert for low temperature (<5°C)"""
    test_data = {
        'main': {'temp': 4, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert "Low temperature warning" in app.alerts[0]

def test_thunderstorm_alert(app):
    """Test alert for thunderstorm conditions"""
    test_data = {
        'main': {'temp': 20, 'humidity': 50},
        'weather': [{'main': 'Thunderstorm'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert "Weather alert: Thunderstorm" in app.alerts[0]

def test_extreme_weather_alert(app):
    """Test alert for extreme weather conditions"""
    test_data = {
        'main': {'temp': 20, 'humidity': 50},
        'weather': [{'main': 'Extreme'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert "Weather alert: Extreme" in app.alerts[0]

def test_high_wind_alert(app):
    """Test alert for high wind (>10 m/s)"""
    test_data = {
        'main': {'temp': 20, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 11},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert "High wind warning" in app.alerts[0]

def test_multiple_alerts(app):
    """Test multiple alerts can be generated simultaneously"""
    test_data = {
        'main': {'temp': 36, 'humidity': 50},
        'weather': [{'main': 'Thunderstorm'}],
        'wind': {'speed': 11},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert len(app.alerts) == 3
    assert "High temperature warning" in app.alerts[0]
    assert "Weather alert: Thunderstorm" in app.alerts[1]
    assert "High wind warning" in app.alerts[2]

def test_alerts_button_style_changes(app):
    """Test alerts button style changes when alerts exist"""
    test_data = {
        'main': {'temp': 36, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert app.alerts_btn.cget('style') == 'Warning.TButton'

def test_no_alerts_button_style(app):
    """Test alerts button style remains normal when no alerts"""
    test_data = {
        'main': {'temp': 20, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert app.alerts_btn.cget('style') == 'TButton'

def test_notification_generated_for_alerts(app, monkeypatch):
    """Test notification is generated when alerts exist"""
    mock_notify = MagicMock()
    monkeypatch.setattr("plyer.notification.notify", mock_notify)
    
    test_data = {
        'main': {'temp': 36, 'humidity': 50},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    mock_notify.assert_called_once()
def test_incomplete_weather_data(app):
    """Fail: Test with incomplete weather data (missing 'main' section)"""
    test_data = {
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    try:
        app.check_weather_alerts(test_data)
        assert False, "Expected KeyError for missing 'main'"
    except KeyError:
        assert True  # expected behavior

def test_unexpected_weather_condition(app):
    """Fail: Test with an unexpected weather condition (e.g., 'Alien Invasion')"""
    test_data = {
        'main': {'temp': 20, 'humidity': 50},
        'weather': [{'main': 'Alien Invasion'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    # This should not raise an alert, but might depending on how unknown conditions are handled
    assert len(app.alerts) == 0, "Unexpected alert for unrecognized weather condition"
