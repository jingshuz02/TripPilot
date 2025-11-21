"""
天气组件 - 改进版
新功能：
1. 🌤️ 主天气大显示（查询当天）
2. 📅 未来天气小卡片显示
3. 更丰富的天气图标
4. 支持DeepSeek返回的天气数据结构
"""

import streamlit as st
from datetime import datetime, timedelta
import random


def get_weather_emoji(condition):
    """根据天气状况返回对应的emoji"""
    weather_emojis = {
        "clear": "☀️", "sunny": "☀️", "晴": "☀️", "晴朗": "☀️",
        "cloudy": "☁️", "多云": "☁️", "阴": "☁️",
        "partly_cloudy": "⛅", "晴转多云": "⛅",
        "rainy": "🌧️", "小雨": "🌧️", "中雨": "🌧️", "大雨": "⛈️",
        "stormy": "⛈️", "雷雨": "⛈️", "雷阵雨": "⛈️",
        "snowy": "🌨️", "雪": "❄️", "小雪": "🌨️",
        "foggy": "🌫️", "雾": "🌫️",
        "windy": "💨", "大风": "💨"
    }

    condition_str = str(condition).lower()
    for key, emoji in weather_emojis.items():
        if key in condition_str:
            return emoji
    return "🌤️"


def display_weather_enhanced(weather_data, city_name=None):
    """
    显示增强版天气信息 - 主天气大显示，未来天气小显示

    参数:
        weather_data: 天气数据字典，必须包含：
            - temperature: 温度
            - feels_like: 体感温度
            - weather/description: 天气描述
            - humidity: 湿度
            - wind_speed: 风速
            - forecast: 未来天气预报数组（可选）
        city_name: 城市名称（可选）
    """

    # CSS样式 - 使用浅绿色
    st.markdown("""
    <style>
    /* 主天气卡片 - 大卡片 */
    .weather-card-main {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin: 16px 0;
        box-shadow: 0 8px 30px rgba(16, 185, 129, 0.4);
    }
    
    .weather-city-name {
        font-size: 20px;
        font-weight: 600;
        opacity: 0.95;
        margin-bottom: 12px;
    }
    
    .weather-main-display {
        text-align: center;
        margin: 20px 0;
    }
    
    .weather-icon-large {
        font-size: 96px;
        margin: 12px 0;
        filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
    }
    
    .weather-temp-large {
        font-size: 72px;
        font-weight: 800;
        line-height: 1;
        margin: 12px 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .weather-desc-text {
        font-size: 24px;
        opacity: 0.95;
        font-weight: 500;
    }
    
    /* 未来天气小卡片 */
    .forecast-small-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.2s ease;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .forecast-small-card:hover {
        border-color: #10b981;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.15);
        transform: translateY(-2px);
    }
    
    .forecast-date {
        font-size: 13px;
        color: #6b7280;
        font-weight: 500;
        margin-bottom: 8px;
    }
    
    .forecast-icon {
        font-size: 48px;
        margin: 12px 0;
    }
    
    .forecast-temp {
        font-size: 18px;
        font-weight: 700;
        color: #10b981;
        margin: 8px 0;
    }
    
    .forecast-desc {
        font-size: 12px;
        color: #9ca3af;
    }
    </style>
    """, unsafe_allow_html=True)


    # 提取数据
    if not city_name:
        city_name = weather_data.get('city', weather_data.get('location', '城市'))

    temp = weather_data.get('temperature', 20)
    feels_like = weather_data.get('feels_like', temp)
    desc = weather_data.get('weather', weather_data.get('description', '晴朗'))
    humidity = weather_data.get('humidity', 60)
    wind_speed = weather_data.get('wind_speed', '3.0 m/s')

    # 确保wind_speed是字符串
    if not isinstance(wind_speed, str):
        wind_speed = f"{wind_speed} m/s"

    icon = get_weather_emoji(desc)

    # 生成天气建议
    if temp > 30:
        advice = "☀️ 天气炎热，请注意防暑降温，多喝水，避免长时间户外活动"
    elif temp > 25:
        advice = "🌤️ 天气温暖舒适，适合外出游玩，建议做好防晒"
    elif temp > 15:
        advice = "😊 温度适宜，非常适合户外活动和旅行"
    elif temp > 10:
        advice = "🧥 天气稍凉，建议携带外套以备不时之需"
    elif temp > 0:
        advice = "🥶 天气较冷，请注意保暖，建议穿着厚外套"
    else:
        advice = "❄️ 天气寒冷，请做好防寒措施，注意保暖"

    # 根据天气添加额外建议
    if '雨' in desc:
        advice += " | 记得带伞 ☔"
    elif '雪' in desc:
        advice += " | 路面可能湿滑，注意安全 ⚠️"
    elif '风' in desc or (wind_speed and float(wind_speed.split()[0]) > 5):
        advice += " | 风力较大，注意防风 💨"

    # ===== 主天气卡片 - 大显示 =====
    st.markdown(f"""
    <div class='weather-card-main'>
        <div class='weather-city-name'>📍 {city_name} · 实时天气</div>
        <div class='weather-main-display'>
            <div class='weather-icon-large'>{icon}</div>
            <div class='weather-temp-large'>{temp}°C</div>
            <div class='weather-desc-text'>{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===== 详细信息 - 使用Streamlit原生组件 =====
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🌡️ 体感温度", f"{feels_like}°C")

    with col2:
        st.metric("💧 湿度", f"{humidity}%")

    with col3:
        st.metric("💨 风速", wind_speed)

    with col4:
        air_quality = weather_data.get('air_quality', '良好')
        st.metric("🍃 空气质量", air_quality)

    # 出行建议
    st.info(f"**💡 出行建议：** {advice}")

    st.divider()

    # ===== 未来天气预报 - 小卡片显示 =====
    forecast_data = weather_data.get('forecast', [])

    if forecast_data and len(forecast_data) > 0:
        st.markdown("### 📅 未来天气预报")
        st.caption("未来几天天气趋势")

        # 显示forecast数据 - 使用小卡片
        cols = st.columns(min(len(forecast_data), 4))

        for idx, (col, day) in enumerate(zip(cols, forecast_data[:4])):
            with col:
                day_icon = get_weather_emoji(day.get('description', day.get('weather', '晴')))
                day_date = day.get('date', f'Day {idx+1}')
                temp_high = day.get('temp_high', 'N/A')
                temp_low = day.get('temp_low', 'N/A')
                day_desc = day.get('description', day.get('weather', 'N/A'))

                st.markdown(f"""
                <div class='forecast-small-card'>
                    <div class='forecast-date'>{day_date}</div>
                    <div class='forecast-icon'>{day_icon}</div>
                    <div class='forecast-temp'>{temp_high}° / {temp_low}°</div>
                    <div class='forecast-desc'>{day_desc}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        # 如果没有forecast数据，生成mock数据作为fallback
        st.markdown("### 📅 未来天气预报")
        st.caption("⚠️ 预报数据暂时不可用，显示示例数据")

        forecast_data = get_mock_forecast_data(4)
        cols = st.columns(4)

        for idx, (col, day) in enumerate(zip(cols, forecast_data)):
            with col:
                day_icon = get_weather_emoji(day['description'])
                st.markdown(f"""
                <div class='forecast-small-card'>
                    <div class='forecast-date'>{day['date']}</div>
                    <div class='forecast-icon'>{day_icon}</div>
                    <div class='forecast-temp'>{day['temp_high']}° / {day['temp_low']}°</div>
                    <div class='forecast-desc'>{day['description']}</div>
                </div>
                """, unsafe_allow_html=True)

    # 额外信息（如果有）
    if weather_data.get('sunrise') or weather_data.get('sunset'):
        st.divider()
        col_sun1, col_sun2 = st.columns(2)

        with col_sun1:
            if weather_data.get('sunrise'):
                st.markdown(f"🌅 **日出：** {weather_data.get('sunrise')}")

        with col_sun2:
            if weather_data.get('sunset'):
                st.markdown(f"🌇 **日落：** {weather_data.get('sunset')}")


def get_mock_forecast_data(days=4):
    """获取模拟预报数据（仅在没有真实数据时使用）"""
    forecast = []
    weather_options = ["晴", "多云", "阴", "小雨", "晴转多云"]

    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
        date_str = f"{date.month}/{date.day} {weekday}"

        forecast.append({
            "date": date_str,
            "temp_high": random.randint(20, 30),
            "temp_low": random.randint(15, 22),
            "description": random.choice(weather_options),
            "weather": random.choice(weather_options)
        })

    return forecast


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="天气组件测试", layout="wide")

    st.title("🌤️ 天气组件测试 - 主天气大显示")
    st.caption("当天天气大卡片，未来天气小卡片")

    # 测试数据1: 完整的DeepSeek数据格式
    test_weather_deepseek = {
        'city': '成都',
        'location': '成都',
        'temperature': 18,
        'feels_like': 16,
        'weather': '多云',
        'description': '多云',
        'humidity': 70,
        'wind_speed': '2.5 m/s',
        'wind_direction': '东南风',
        'visibility': '12 km',
        'pressure': '1015 hPa',
        'uv_index': 3,
        'sunrise': '07:15',
        'sunset': '18:30',
        'update_time': '2025-11-21 14:30',
        'air_quality': '良',
        'forecast': [
            {
                'date': '11/22 周五',
                'temp_high': 20,
                'temp_low': 14,
                'weather': '晴',
                'description': '晴'
            },
            {
                'date': '11/23 周六',
                'temp_high': 22,
                'temp_low': 15,
                'weather': '多云',
                'description': '多云'
            },
            {
                'date': '11/24 周日',
                'temp_high': 19,
                'temp_low': 13,
                'weather': '小雨',
                'description': '小雨'
            },
            {
                'date': '11/25 周一',
                'temp_high': 21,
                'temp_low': 14,
                'weather': '晴转多云',
                'description': '晴转多云'
            }
        ]
    }

    st.subheader("测试1: 完整的DeepSeek数据（主天气+4天预报）")
    display_weather_enhanced(test_weather_deepseek)

    st.divider()

    # 测试数据2: 不同温度和天气
    test_weather_hot = {
        'city': '三亚',
        'temperature': 32,
        'feels_like': 35,
        'weather': '晴',
        'humidity': 80,
        'wind_speed': '3.5 m/s',
        'air_quality': '优',
        'forecast': [
            {'date': '明天', 'temp_high': 33, 'temp_low': 26, 'description': '晴'},
            {'date': '后天', 'temp_high': 34, 'temp_low': 27, 'description': '晴'},
        ]
    }

    st.subheader("测试2: 炎热天气")
    display_weather_enhanced(test_weather_hot)

    st.divider()

    # 测试数据3: 寒冷天气
    test_weather_cold = {
        'city': '哈尔滨',
        'temperature': -5,
        'feels_like': -8,
        'weather': '小雪',
        'humidity': 65,
        'wind_speed': '5.0 m/s',
        'air_quality': '良',
        'forecast': [
            {'date': '明天', 'temp_high': -3, 'temp_low': -10, 'description': '多云'},
            {'date': '后天', 'temp_high': -2, 'temp_low': -9, 'description': '晴'},
        ]
    }

    st.subheader("测试3: 寒冷天气")
    display_weather_enhanced(test_weather_cold)