"""
增强版天气组件
增加了更多信息展示
"""

import streamlit as st
from datetime import datetime, timedelta

def get_weather_emoji(condition):
    """根据天气状况返回对应的emoji"""
    weather_emojis = {
        "clear": "☀️", "sunny": "☀️", "晴": "☀️", "晴朗": "☀️",
        "cloudy": "☁️", "多云": "☁️", "阴": "☁️",
        "partly_cloudy": "⛅", "晴转多云": "⛅",
        "rainy": "🌧️", "小雨": "🌧️", "中雨": "🌧️", "大雨": "⛈️",
        "stormy": "⛈️", "雷雨": "⛈️",
        "snowy": "🌨️", "雪": "❄️", "小雪": "🌨️",
        "foggy": "🌫️", "雾": "🌫️",
        "windy": "💨", "大风": "💨"
    }

    for key, emoji in weather_emojis.items():
        if key in str(condition).lower():
            return emoji
    return "🌤️"


def display_weather_enhanced(weather_data, city_name="城市"):
    """
    显示增强版天气信息

    参数:
        weather_data: 天气数据字典
        city_name: 城市名称
    """

    # 美化CSS样式
    st.markdown("""
    <style>
    .weather-enhanced-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 20px;
        color: white;
        margin: 20px 0;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .weather-main-temp {
        font-size: 64px;
        font-weight: 800;
        line-height: 1;
        margin: 20px 0;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    .weather-description {
        font-size: 24px;
        margin-bottom: 10px;
        opacity: 0.95;
    }
    
    .weather-city {
        font-size: 18px;
        opacity: 0.9;
        margin-bottom: 20px;
    }
    
    .weather-detail-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 20px;
        margin-top: 25px;
        padding-top: 25px;
        border-top: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .weather-detail-item {
        background: rgba(255, 255, 255, 0.15);
        padding: 15px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        text-align: center;
    }
    
    .weather-detail-label {
        font-size: 13px;
        opacity: 0.8;
        margin-bottom: 5px;
    }
    
    .weather-detail-value {
        font-size: 22px;
        font-weight: 700;
    }
    
    .weather-advice {
        background: rgba(255, 255, 255, 0.2);
        padding: 15px 20px;
        border-radius: 12px;
        margin-top: 20px;
        font-size: 14px;
        backdrop-filter: blur(10px);
    }
    
    .forecast-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin-top: 20px;
        color: #1f2937;
    }
    
    .forecast-title {
        font-size: 18px;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 15px;
    }
    
    .forecast-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
    }
    
    .forecast-day {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        transition: all 0.3s;
    }
    
    .forecast-day:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .forecast-date {
        font-size: 13px;
        color: #6b7280;
        margin-bottom: 8px;
    }
    
    .forecast-icon {
        font-size: 32px;
        margin: 8px 0;
    }
    
    .forecast-temp {
        font-size: 16px;
        font-weight: 700;
        color: #667eea;
    }
    
    .forecast-desc {
        font-size: 12px;
        color: #9ca3af;
        margin-top: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 提取数据
    temp = weather_data.get('temperature', 20)
    feels_like = weather_data.get('feels_like', temp)
    desc = weather_data.get('weather', weather_data.get('description', '晴朗'))
    humidity = weather_data.get('humidity', 60)
    wind_speed = weather_data.get('wind_speed', '3.0 m/s')

    # 如果wind_speed不是字符串，转换为字符串
    if not isinstance(wind_speed, str):
        wind_speed = f"{wind_speed} m/s"

    icon = get_weather_emoji(desc)

    # 生成天气建议
    if temp > 30:
        advice = "🌡️ 天气炎热，请注意防暑降温，多喝水，避免长时间户外活动"
    elif temp > 25:
        advice = "☀️ 天气温暖舒适，适合外出游玩，建议做好防晒"
    elif temp > 15:
        advice = "🌤️ 温度适宜，非常适合户外活动和旅行"
    elif temp > 10:
        advice = "🧥 天气稍凉，建议携带外套以备不时之需"
    elif temp > 0:
        advice = "🧤 天气较冷，请注意保暖，建议穿着厚外套"
    else:
        advice = "🥶 天气寒冷，请做好防寒措施，注意保暖"

    # 根据天气添加额外建议
    if '雨' in desc:
        advice += "。记得带伞！"
    elif '雪' in desc:
        advice += "。路面可能湿滑，注意安全！"
    elif '风' in desc or float(wind_speed.split()[0]) > 5:
        advice += "。风力较大，注意防风！"

    # 渲染主天气卡片
    st.markdown(f"""
    <div class='weather-enhanced-card'>
        <div class='weather-city'>📍 {city_name}</div>
        <div style='text-align: center;'>
            <div style='font-size: 80px;'>{icon}</div>
            <div class='weather-main-temp'>{temp}°C</div>
            <div class='weather-description'>{desc}</div>
        </div>
        
        <div class='weather-detail-grid'>
            <div class='weather-detail-item'>
                <div class='weather-detail-label'>体感温度</div>
                <div class='weather-detail-value'>{feels_like}°C</div>
            </div>
            <div class='weather-detail-item'>
                <div class='weather-detail-label'>湿度</div>
                <div class='weather-detail-value'>{humidity}%</div>
            </div>
            <div class='weather-detail-item'>
                <div class='weather-detail-label'>风速</div>
                <div class='weather-detail-value'>{wind_speed}</div>
            </div>
            <div class='weather-detail-item'>
                <div class='weather-detail-label'>空气质量</div>
                <div class='weather-detail-value'>良好</div>
            </div>
        </div>
        
        <div class='weather-advice'>
            <strong>出行建议：</strong> {advice}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 未来天气预报
    forecast_data = get_mock_forecast_data(4)

    st.markdown("""
    <div class='forecast-container'>
        <div class='forecast-title'>📅 未来4天预报</div>
        <div class='forecast-grid'>
    """, unsafe_allow_html=True)

    for day in forecast_data:
        date_str = day['date']
        temp_high = day['temp_high']
        temp_low = day['temp_low']
        day_desc = day['description']
        day_icon = get_weather_emoji(day_desc)

        st.markdown(f"""
        <div class='forecast-day'>
            <div class='forecast-date'>{date_str}</div>
            <div class='forecast-icon'>{day_icon}</div>
            <div class='forecast-temp'>{temp_high}° / {temp_low}°</div>
            <div class='forecast-desc'>{day_desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)


def get_mock_forecast_data(days=4):
    """获取模拟预报数据"""
    import random

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
            "icon": random.choice(["clear", "cloudy", "partly_cloudy", "rainy"])
        })

    return forecast


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="增强版天气组件", layout="wide")

    st.title("增强版天气组件测试")

    test_weather = {
        'temperature': 22,
        'feels_like': 20,
        'weather': '晴朗',
        'humidity': 65,
        'wind_speed': '3.5 m/s'
    }

    display_weather_enhanced(test_weather, "北京")