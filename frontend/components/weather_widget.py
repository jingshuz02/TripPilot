"""
修复版天气组件 - 简化emoji，修复HTML渲染问题
"""

import streamlit as st
from datetime import datetime, timedelta
import random


def get_weather_emoji(condition):
    """根据天气状况返回对应的emoji"""
    weather_emojis = {
        "clear": "☀", "sunny": "☀", "晴": "☀", "晴朗": "☀",
        "cloudy": "☁", "多云": "☁", "阴": "☁",
        "partly_cloudy": "⛅", "晴转多云": "⛅",
        "rainy": "🌧", "小雨": "🌧", "中雨": "🌧", "大雨": "⛈",
        "stormy": "⛈", "雷雨": "⛈",
        "snowy": "🌨", "雪": "❄", "小雪": "🌨",
        "foggy": "🌫", "雾": "🌫",
        "windy": "💨", "大风": "💨"
    }

    for key, emoji in weather_emojis.items():
        if key in str(condition).lower():
            return emoji
    return "🌤"


def display_weather_enhanced(weather_data, city_name="城市"):
    """
    显示增强版天气信息 - 修复版

    参数:
        weather_data: 天气数据字典
        city_name: 城市名称
    """

    # 修复后的CSS样式 - 使用浅绿色
    st.markdown("""
    <style>
    .weather-card-fixed {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 25px;
        border-radius: 16px;
        color: white;
        margin: 16px 0;
        box-shadow: 0 4px 20px rgba(16, 185, 129, 0.3);
    }
    
    .weather-city-name {
        font-size: 16px;
        opacity: 0.95;
        margin-bottom: 12px;
    }
    
    .weather-main-display {
        text-align: center;
        margin: 16px 0;
    }
    
    .weather-icon-large {
        font-size: 72px;
        margin: 8px 0;
    }
    
    .weather-temp-large {
        font-size: 56px;
        font-weight: 800;
        line-height: 1;
        margin: 12px 0;
    }
    
    .weather-desc-text {
        font-size: 20px;
        opacity: 0.95;
    }
    
    .weather-details-container {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
        margin-top: 20px;
        padding-top: 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .weather-detail-box {
        background: rgba(255, 255, 255, 0.15);
        padding: 12px;
        border-radius: 10px;
        text-align: center;
    }
    
    .weather-detail-title {
        font-size: 13px;
        opacity: 0.8;
        margin-bottom: 4px;
    }
    
    .weather-detail-content {
        font-size: 20px;
        font-weight: 700;
    }
    
    .weather-advice-box {
        background: rgba(255, 255, 255, 0.2);
        padding: 14px 18px;
        border-radius: 10px;
        margin-top: 16px;
        font-size: 14px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)

    # 提取数据
    temp = weather_data.get('temperature', 20)
    feels_like = weather_data.get('feels_like', temp)
    desc = weather_data.get('weather', weather_data.get('description', '晴朗'))
    humidity = weather_data.get('humidity', 60)
    wind_speed = weather_data.get('wind_speed', '3.0 m/s')

    # 确保wind_speed是字符串
    if not isinstance(wind_speed, str):
        wind_speed = f"{wind_speed} m/s"

    icon = get_weather_emoji(desc)

    # 生成天气建议（简化版）
    if temp > 30:
        advice = "天气炎热，请注意防暑降温，多喝水，避免长时间户外活动"
    elif temp > 25:
        advice = "天气温暖舒适，适合外出游玩，建议做好防晒"
    elif temp > 15:
        advice = "温度适宜，非常适合户外活动和旅行"
    elif temp > 10:
        advice = "天气稍凉，建议携带外套以备不时之需"
    elif temp > 0:
        advice = "天气较冷，请注意保暖，建议穿着厚外套"
    else:
        advice = "天气寒冷，请做好防寒措施，注意保暖"

    # 根据天气添加额外建议
    if '雨' in desc:
        advice += "。记得带伞"
    elif '雪' in desc:
        advice += "。路面可能湿滑，注意安全"
    elif '风' in desc or float(wind_speed.split()[0]) > 5:
        advice += "。风力较大，注意防风"

    # 使用Streamlit原生组件渲染，避免HTML问题
    st.markdown(f"""
    <div class='weather-card-fixed'>
        <div class='weather-city-name'>{city_name}</div>
        <div class='weather-main-display'>
            <div class='weather-icon-large'>{icon}</div>
            <div class='weather-temp-large'>{temp}°C</div>
            <div class='weather-desc-text'>{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 使用Streamlit原生组件显示详细信息
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("体感温度", f"{feels_like}°C")

    with col2:
        st.metric("湿度", f"{humidity}%")

    with col3:
        st.metric("风速", wind_speed)

    with col4:
        st.metric("空气质量", "良好")

    # 出行建议
    st.info(f"**出行建议：** {advice}")

    # 未来天气预报 - 使用简化版本
    st.markdown("### 未来4天预报")

    forecast_data = get_mock_forecast_data(4)

    cols = st.columns(4)
    for idx, (col, day) in enumerate(zip(cols, forecast_data)):
        with col:
            day_icon = get_weather_emoji(day['description'])
            st.markdown(f"""
            <div style='text-align: center; padding: 12px; background: #f3f4f6; 
                        border-radius: 10px; border: 1px solid #e5e7eb;'>
                <div style='font-size: 12px; color: #6b7280; margin-bottom: 6px;'>
                    {day['date']}
                </div>
                <div style='font-size: 36px; margin: 8px 0;'>{day_icon}</div>
                <div style='font-size: 15px; font-weight: 600; color: #10b981;'>
                    {day['temp_high']}° / {day['temp_low']}°
                </div>
                <div style='font-size: 11px; color: #9ca3af; margin-top: 4px;'>
                    {day['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)


def get_mock_forecast_data(days=4):
    """获取模拟预报数据"""
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
        })

    return forecast


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="修复版天气组件", layout="wide")

    st.title("修复版天气组件测试")

    test_weather = {
        'temperature': 22,
        'feels_like': 20,
        'weather': '晴朗',
        'humidity': 65,
        'wind_speed': '3.5 m/s'
    }

    display_weather_enhanced(test_weather, "北京")