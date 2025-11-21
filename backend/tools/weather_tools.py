# """
# 天气查询工具 - 修复版本
# 修复了API返回格式处理问题
# """
# import requests
# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# class WeatherTool:
#     """天气查询工具类"""

#     def __init__(self, base_url="http://localhost:5000"):
#         """
#         初始化天气工具
#         Args:
#             base_url: Flask后端地址
#         """
#         self.base_url = base_url

#     def get_weather(self, city: str) -> dict:
#         """
#         查询城市天气 - 修复版
#         """
#         try:
#             # 1. 获取实时天气
#             response = requests.get(
#                 f"{self.base_url}/api/weather/current",
#                 params={"city": city},
#                 timeout=5
#             )

#             if response.status_code == 200:
#                 data = response.json()

#                 if data.get("code") == 0:
#                     weather_data = data.get("data", {})

#                     # 2. 获取天气预报
#                     forecast_response = requests.get(
#                         f"{self.base_url}/api/weather/forecast",
#                         params={"city": city, "days": 3},
#                         timeout=5
#                     )

#                     forecast = []
#                     if forecast_response.status_code == 200:
#                         forecast_data = forecast_response.json()
#                         if forecast_data.get("code") == 0:
#                             # 修复：正确获取预报数据
#                             forecast_list = forecast_data.get("data", [])
#                             # 如果data是列表，直接使用
#                             if isinstance(forecast_list, list):
#                                 forecast = forecast_list
#                             # 如果data是字典，可能包含forecasts字段
#                             elif isinstance(forecast_list, dict):
#                                 forecast = forecast_list.get("forecasts", [])

#                     # 整合返回数据
#                     return {
#                         'temperature': weather_data.get('temperature', 'N/A'),
#                         'description': weather_data.get('weather', weather_data.get('description', 'N/A')),
#                         'humidity': weather_data.get('humidity', 'N/A'),
#                         'wind_speed': weather_data.get('windpower', weather_data.get('wind_speed', 'N/A')),
#                         'city': weather_data.get('city', city),
#                         'forecast': forecast,
#                         'success': True
#                     }
#                 else:
#                     return {
#                         'error': data.get('msg', 'Unknown error'),
#                         'success': False
#                     }
#             else:
#                 return {
#                     'error': f'HTTP {response.status_code}',
#                     'success': False
#                 }

#         except requests.exceptions.Timeout:
#             return {
#                 'error': '请求超时，请稍后重试',
#                 'success': False
#             }
#         except Exception as e:
#             return {
#                 'error': str(e),
#                 'success': False
#             }

#     def get_forecast_summary(self, city: str, days: int = 3) -> str:
#         """
#         获取天气预报摘要（纯文本）- 修复版
#         """
#         weather = self.get_weather(city)

#         if not weather.get('success'):
#             return f"无法获取{city}的天气信息: {weather.get('error', '未知错误')}"

#         # 构建摘要
#         summary = f"📍 {weather.get('city', city)}\n"
#         summary += f"🌡️ 当前温度: {weather['temperature']}°C\n"
#         summary += f"☁️ 天气状况: {weather['description']}\n"
#         summary += f"💧 湿度: {weather['humidity']}\n"
#         summary += f"💨 风力: {weather['wind_speed']}\n"

#         # 添加预报
#         if weather.get('forecast'):
#             forecast_list = weather['forecast']
#             summary += f"\n📅 未来{len(forecast_list)}天预报:\n"
#             for day in forecast_list[:days]:
#                 # 兼容不同的字段名
#                 date = day.get('date', 'N/A')
#                 day_weather = day.get('day_weather', day.get('dayweather', 'N/A'))
#                 max_temp = day.get('max_temp', day.get('daytemp', 'N/A'))
#                 min_temp = day.get('min_temp', day.get('nighttemp', 'N/A'))

#                 summary += f"  • {date}: {day_weather}, {min_temp}~{max_temp}°C\n"

#         return summary


# # 测试代码
# if __name__ == "__main__":
#     tool = WeatherTool()

#     print("=" * 50)
#     print("测试修复后的天气工具")
#     print("=" * 50)

#     # 测试北京天气
#     result = tool.get_weather("北京")
#     if result.get('success'):
#         print("\n✅ 查询成功:")
#         print(f"温度: {result['temperature']}°C")
#         print(f"天气: {result['description']}")
#         print(f"预报数量: {len(result.get('forecast', []))}")
#     else:
#         print(f"\n❌ 查询失败: {result.get('error')}")

#     print("\n文本摘要:")
#     print(tool.get_forecast_summary("北京"))



"""
Weather Query Tool - Fixed Version
Fixes issues with API response format handling.
"""
import requests
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class WeatherTool:
    """Weather Query Tool Class"""

    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize Weather Tool
        Args:
            base_url: Flask backend address
        """
        self.base_url = base_url

    def get_weather(self, city: str) -> dict:
        """
        Query City Weather - Fixed Version
        """
        try:
            # 1. Get current weather
            response = requests.get(
                f"{self.base_url}/api/weather/current",
                params={"city": city},
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("code") == 0:
                    weather_data = data.get("data", {})

                    # 2. Get weather forecast
                    forecast_response = requests.get(
                        f"{self.base_url}/api/weather/forecast",
                        params={"city": city, "days": 3},
                        timeout=5
                    )

                    forecast = []
                    if forecast_response.status_code == 200:
                        forecast_data = forecast_response.json()
                        if forecast_data.get("code") == 0:
                            # Fix: Correctly retrieve forecast data
                            forecast_list = forecast_data.get("data", [])
                            # If data is a list, use it directly
                            if isinstance(forecast_list, list):
                                forecast = forecast_list
                            # If data is a dictionary, it might contain a 'forecasts' field
                            elif isinstance(forecast_list, dict):
                                forecast = forecast_list.get("forecasts", [])

                    # Consolidate and return data
                    return {
                        'temperature': weather_data.get('temperature', 'N/A'),
                        'description': weather_data.get('weather', weather_data.get('description', 'N/A')),
                        'humidity': weather_data.get('humidity', 'N/A'),
                        'wind_speed': weather_data.get('windpower', weather_data.get('wind_speed', 'N/A')),
                        'city': weather_data.get('city', city),
                        'forecast': forecast,
                        'success': True
                    }
                else:
                    return {
                        'error': data.get('msg', 'Unknown error'),
                        'success': False
                    }
            else:
                return {
                    'error': f'HTTP {response.status_code}',
                    'success': False
                }

        except requests.exceptions.Timeout:
            return {
                'error': 'Request timed out, please try again later',
                'success': False
            }
        except Exception as e:
            return {
                'error': str(e),
                'success': False
            }

    def get_forecast_summary(self, city: str, days: int = 3) -> str:
        """
        Get weather forecast summary (plain text) - Fixed Version
        """
        weather = self.get_weather(city)

        if not weather.get('success'):
            return f"Unable to fetch weather information for {city}: {weather.get('error', 'Unknown Error')}"

        # Build summary
        summary = f"📍 {weather.get('city', city)}\n"
        summary += f"🌡️ Current Temperature: {weather['temperature']}°C\n"
        summary += f"☁️ Weather Condition: {weather['description']}\n"
        summary += f"💧 Humidity: {weather['humidity']}\n"
        summary += f"💨 Wind Speed: {weather['wind_speed']}\n"

        # Add forecast
        if weather.get('forecast'):
            forecast_list = weather['forecast']
            summary += f"\n📅 {len(forecast_list)} Day Forecast:\n"
            for day in forecast_list[:days]:
                # Compatibility with different field names
                date = day.get('date', 'N/A')
                day_weather = day.get('day_weather', day.get('dayweather', 'N/A'))
                max_temp = day.get('max_temp', day.get('daytemp', 'N/A'))
                min_temp = day.get('min_temp', day.get('nighttemp', 'N/A'))

                summary += f"  • {date}: {day_weather}, {min_temp}~{max_temp}°C\n"

        return summary


# Testing code
if __name__ == "__main__":
    tool = WeatherTool()

    print("=" * 50)
    print("Testing Fixed Weather Tool")
    print("=" * 50)

    # Test Beijing weather
    result = tool.get_weather("Beijing")
    if result.get('success'):
        print("\n✅ Query Successful:")
        print(f"Temperature: {result['temperature']}°C")
        print(f"Weather: {result['description']}")
        print(f"Forecast Count: {len(result.get('forecast', []))}")
    else:
        print(f"\n❌ Query Failed: {result.get('error')}")

    print("\nText Summary:")
    print(tool.get_forecast_summary("Beijing"))