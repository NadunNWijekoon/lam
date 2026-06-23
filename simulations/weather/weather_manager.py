import random
from config import WEATHER_IMPACT

class WeatherManager:
    def __init__(self):
        self.weather_types = list(WEATHER_IMPACT.keys())
        self.current_weather = "Sunny"
        self.temperature = 25.0  # Celsius

    def set_weather(self, weather_name):
        if weather_name in self.weather_types:
            self.current_weather = weather_name
            # Adjust temperature randomly matching weather type
            if weather_name == "Sunny":
                self.temperature = random.uniform(22.0, 35.0)
            elif weather_name == "Rain":
                self.temperature = random.uniform(15.0, 22.0)
            elif weather_name == "Storm":
                self.temperature = random.uniform(14.0, 20.0)
            elif weather_name == "Fog":
                self.temperature = random.uniform(10.0, 18.0)
            elif weather_name == "Snow":
                self.temperature = random.uniform(-10.0, 2.0)
            return True
        return False

    def get_impact_factors(self):
        """Returns the dictionary of impact factors for the current weather."""
        return WEATHER_IMPACT[self.current_weather]

    def update_temperature(self):
        """Slightly fluctuate temperature over time."""
        fluctuation = random.uniform(-0.1, 0.1)
        self.temperature = max(-15.0, min(45.0, self.temperature + fluctuation))

    def get_status(self):
        return {
            "weather": self.current_weather,
            "temperature": round(self.temperature, 1)
        }
