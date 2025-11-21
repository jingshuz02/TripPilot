import requests
from config.config import Config
import re

"""- Query current weather
   - 5-day weather forecast
   - Recommend activities based on weather"""

class WeatherAPI:
    """
    Amap weather API encapsulation
    - Real-time weather /api/weather/current?city=Shanghai
    - 4-day forecast /api/weather/forecast?city=Shanghai
    """
    def __init__(self):
        self.api_key = Config.GAODE_API_KEY  # Shares the same key with the map module
        self.base_url = "https://restapi.amap.com/v3/weather"

    # --------- Public methods ---------
    def get_current_weather(self, city: str):
        """Real-time weather"""
        payload = {"key": self.api_key, "city": city, "extensions": "base"}
        rsp = requests.get(f"{self.base_url}/weatherInfo", params=payload)
        return self._fmt_live(rsp.json())

    def get_forecast(self, city: str, days: int = 4):
        """4-day forecast (Amap only supports 4 days)"""
        payload = {"key": self.api_key, "city": city, "extensions": "all"}
        rsp = requests.get(f"{self.base_url}/weatherInfo", params=payload)
        return self._fmt_forecast(rsp.json(), days)

    # --------- Internal formatting ---------
    def _fmt_live(self, js: dict):
        """Format real-time weather (Amap version)"""
        if int(js.get("status", 0)) != 1 or "lives" not in js or not js["lives"]:
            raise RuntimeError("Amap weather - real-time interface exception: " + str(js))
        live = js["lives"][0]

        # Parse wind force level, default to 0 if non-numeric
        wind_level = 0.0
        m = re.search(r"\d+", live.get("windpower", ""))
        if m:
            wind_level = float(m.group(0))

        return {
            "temperature": float(live["temperature"]),
            # "feels_like": float(live["temperature"]),  # Amap has no feels-like temperature, use temperature directly
            "description": live["weather"],
            "humidity": float(live["humidity"]),
            "wind_speed": wind_level,
        }

    def _fmt_forecast(self, js: dict, days: int):
        """Format forecast - Chinese character version"""
        if int(js.get("status", 0)) != 1 or "forecasts" not in js or not js["forecasts"]:
            raise RuntimeError("Amap weather - forecast interface exception: " + str(js))
        casts = js["forecasts"][0]["casts"]
        out = []
        for c in casts[:days]:
            out.append({
                "date": c["date"],
                "day_weather": c["dayweather"],
                "night_weather": c["nightweather"],
                "min_temp": int(c["nighttemp"]),  # Convert directly to int without unpacking
                "max_temp": int(c["daytemp"]),
            })
        return out