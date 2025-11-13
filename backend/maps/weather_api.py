import requests
from config.config import Config
import re

"""- 查询当前天气
   - 5天天气预报
   - 根据天气推荐活动"""

class WeatherAPI:
    """
    高德天气接口封装
    - 实时天气 /api/weather/current?city=上海
    - 未来 4 天预报 /api/weather/forecast?city=上海
    """
    def __init__(self):
        self.api_key = Config.GAODE_API_KEY   # 与地图模块共用同一个 key
        self.base_url = "https://restapi.amap.com/v3/weather"

    # --------- 对外方法 ---------
    def get_current_weather(self, city: str):
        """实时天气"""
        payload = {"key": self.api_key, "city": city, "extensions": "base"}
        rsp = requests.get(f"{self.base_url}/weatherInfo", params=payload)
        return self._fmt_live(rsp.json())

    def get_forecast(self, city: str, days: int = 4):
        """未来 4 天预报（高德只支持 4 天）"""
        payload = {"key": self.api_key, "city": city, "extensions": "all"}
        rsp = requests.get(f"{self.base_url}/weatherInfo", params=payload)
        return self._fmt_forecast(rsp.json(), days)

    # --------- 内部格式化 ---------
    def _fmt_live(self, js: dict):
        """格式化实时天气（高德版）"""
        if int(js.get("status", 0)) != 1 or "lives" not in js or not js["lives"]:
            raise RuntimeError("高德天气-实时接口异常:" + str(js))
        live = js["lives"][0]

        # 解析风力等级，非数字则默认 0
        wind_level = 0.0
        m = re.search(r"\d+", live.get("windpower", ""))
        if m:
            wind_level = float(m.group(0))

        return {
            "temperature": float(live["temperature"]),
            # "feels_like": float(live["temperature"]),  # 高德无体感，直接用气温
            "description": live["weather"],
            "humidity": float(live["humidity"]),
            "wind_speed": wind_level,
        }

    def _fmt_forecast(self, js: dict, days: int):
        """格式化预报——汉字版"""
        if int(js.get("status", 0)) != 1 or "forecasts" not in js or not js["forecasts"]:
            raise RuntimeError("高德天气-预报接口异常:" + str(js))
        casts = js["forecasts"][0]["casts"]
        out = []
        for c in casts[:days]:
            out.append({
                "date": c["date"],
                "day_weather": c["dayweather"],
                "night_weather": c["nightweather"],
                "min_temp": int(c["nighttemp"]),  # 直接转 int，不拆包
                "max_temp": int(c["daytemp"]),
            })
        return out