import pytest
from src.gui import WeatherApp

@pytest.fixture
def app():
    return WeatherApp()

# Temperature Tests
@pytest.mark.parametrize("temp,expected", [
    (4.9, True), (5.0, False), (5.1, False),    # Low temp boundary
    (34.9, False), (35.0, False), (35.1, True)  # High temp boundary
])
def test_temp_boundaries(app, temp, expected):
    test_data = {
        'main': {'temp': temp},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert ("temperature warning" in '\n'.join(app.alerts)) == expected

# Wind Speed Tests
@pytest.mark.parametrize("wind,expected", [
    (9.9, False), (10.0, False), (10.1, True)
])
def test_wind_boundaries(app, wind, expected):
    test_data = {
        'main': {'temp': 20},
        'weather': [{'main': 'Clear'}],
        'wind': {'speed': wind},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert ("wind warning" in '\n'.join(app.alerts)) == expected

# Weather Condition Tests
@pytest.mark.parametrize("condition,expected_alert", [
    ("Thunderstorm", True),
    ("Extreme", True),
    ("Clear", False),
    ("Rain", False)
])
def test_weather_conditions(app, condition, expected_alert):
    test_data = {
        'main': {'temp': 20},
        'weather': [{'main': condition}],
        'wind': {'speed': 5},
        'sys': {}
    }
    app.check_weather_alerts(test_data)
    assert any("Weather alert" in alert for alert in app.alerts) == expected_alert

# Edge Cases
def test_empty_weather_data(app):
    with pytest.raises(IndexError):
        app.check_weather_alerts({'weather': []})

def test_negative_wind_speed(app):
    with pytest.raises(ValueError):
        app.check_weather_alerts({'wind': {'speed': -5}})