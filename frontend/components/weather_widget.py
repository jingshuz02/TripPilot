import streamlit as st
from datetime import datetime, timedelta

def get_weather_emoji(condition):
    """根据天气状况返回对应的emoji"""
    weather_emojis = {
        "clear": "☀️",
        "sunny": "☀️",
        "cloudy": "☁️",
        "partly_cloudy": "⛅",
        "rainy": "🌧️",
        "stormy": "⛈️",
        "snowy": "🌨️",
        "foggy": "🌫️",
        "windy": "💨"
    }
    return weather_emojis.get(condition.lower(), "🌤️")


def display_weather_compact(weather_data, city_name="Tokyo", forecast_days=4):
    """
    显示紧凑版天气组件（适合侧边栏）
    
    参数:
        weather_data (dict): 当前天气数据
        city_name (str): 城市名称
        forecast_days (int): 预报天数（1-4天）
    """
    
    # 清新蓝色主题 CSS
    st.markdown("""
    <style>
    .weather-compact {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 12px;
        border-radius: 10px;
        color: white;
        margin-bottom: 10px;
    }
    .weather-temp-compact {
        font-size: 28px;
        font-weight: bold;
        margin: 3px 0;
    }
    .weather-desc-compact {
        font-size: 13px;
        opacity: 0.9;
    }
    .weather-detail-compact {
        font-size: 11px;
        opacity: 0.8;
        margin-top: 5px;
    }
    .forecast-mini {
        background: #f0f7ff;
        border: 1px solid #bee3f8;
        border-radius: 6px;
        padding: 8px;
        margin: 4px 0;
        font-size: 12px;
    }
    .forecast-mini-date {
        font-weight: bold;
        color: #2b6cb0;
    }
    .forecast-mini-temp {
        color: #2c5282;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 提取当前天气数据
    temp = weather_data.get('temperature', 0)
    feels_like = weather_data.get('feels_like', 0)
    desc = weather_data.get('description', '晴朗')
    humidity = weather_data.get('humidity', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    icon = weather_data.get('icon', 'clear')
    
    emoji = get_weather_emoji(icon)
    
    # 当前天气卡片（紧凑版）
    st.markdown(f"""
    <div class='weather-compact'>
        <div style='text-align: center;'>
            <div style='font-size: 36px;'>{emoji}</div>
            <div class='weather-temp-compact'>{temp}°C</div>
            <div class='weather-desc-compact'>{desc}</div>
            <div class='weather-detail-compact'>
                💧 {humidity}% · 💨 {wind_speed} m/s
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 选择预报天数
    st.caption("📅 未来天气预报")
    selected_days = st.slider(
        "选择天数",
        min_value=1,
        max_value=4,
        value=min(forecast_days, 4),
        key=f"forecast_days_{city_name}",
        label_visibility="collapsed"
    )
    
    # 生成未来天气预报
    forecast = get_mock_forecast_data(selected_days)
    
    for day in forecast:
        date_str = day['date']
        temp_high = day['temp_high']
        temp_low = day['temp_low']
        desc = day['description']
        icon = day['icon']
        emoji = get_weather_emoji(icon)
        
        st.markdown(f"""
        <div class='forecast-mini'>
            <span class='forecast-mini-date'>{date_str}</span>
            <span style='margin: 0 5px;'>{emoji}</span>
            <span class='forecast-mini-temp'>{temp_high}° / {temp_low}°</span>
            <span style='color: #718096; margin-left: 5px;'>{desc}</span>
        </div>
        """, unsafe_allow_html=True)


def display_weather(weather_data, city_name="Tokyo"):
    """
    显示完整天气信息（用于主页面）
    
    参数:
        weather_data (dict): 天气数据
        city_name (str): 城市名称
    """
    
    # 清新蓝色主题 CSS
    st.markdown("""
    <style>
    .weather-container {
        background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .weather-temp {
        font-size: 42px;
        font-weight: bold;
        margin: 8px 0;
    }
    .weather-desc {
        font-size: 18px;
        opacity: 0.95;
    }
    .weather-detail {
        font-size: 14px;
        opacity: 0.9;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 提取数据
    temp = weather_data.get('temperature', 0)
    feels_like = weather_data.get('feels_like', 0)
    desc = weather_data.get('description', '晴朗')
    humidity = weather_data.get('humidity', 0)
    wind_speed = weather_data.get('wind_speed', 0)
    icon = weather_data.get('icon', 'clear')
    
    emoji = get_weather_emoji(icon)
    
    # 渲染天气卡片
    st.markdown(f"""
    <div class='weather-container'>
        <div style='text-align: center;'>
            <div style='font-size: 56px;'>{emoji}</div>
            <div class='weather-temp'>{temp}°C</div>
            <div class='weather-desc'>{desc}</div>
            <div class='weather-detail'>
                体感 {feels_like}°C · 💧 {humidity}% · 💨 {wind_speed} m/s
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_mock_weather_data(city_name="Tokyo"):
    """获取模拟天气数据"""
    import random
    
    mock_data = {
        "Tokyo": {
            "temperature": 22,
            "feels_like": 20,
            "description": "晴朗",
            "humidity": 65,
            "wind_speed": 3.5,
            "icon": "clear"
        },
        "Paris": {
            "temperature": 15,
            "feels_like": 13,
            "description": "多云",
            "humidity": 72,
            "wind_speed": 4.2,
            "icon": "cloudy"
        },
        "London": {
            "temperature": 12,
            "feels_like": 10,
            "description": "小雨",
            "humidity": 85,
            "wind_speed": 5.1,
            "icon": "rainy"
        },
        "New York": {
            "temperature": 18,
            "feels_like": 16,
            "description": "晴转多云",
            "humidity": 60,
            "wind_speed": 3.8,
            "icon": "partly_cloudy"
        }
    }
    
    if city_name not in mock_data:
        return {
            "temperature": random.randint(15, 30),
            "feels_like": random.randint(13, 28),
            "description": random.choice(["晴朗", "多云", "阴天", "小雨"]),
            "humidity": random.randint(50, 90),
            "wind_speed": round(random.uniform(2.0, 6.0), 1),
            "icon": random.choice(["clear", "cloudy", "partly_cloudy", "rainy"])
        }
    
    return mock_data[city_name]


def get_mock_forecast_data(days=4):
    """获取模拟预报数据"""
    import random
    
    forecast = []
    for i in range(days):
        date = (datetime.now() + timedelta(days=i+1))
        weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]
        date_str = f"{date.month}/{date.day} {weekday}"
        
        forecast.append({
            "date": date_str,
            "temp_high": random.randint(20, 30),
            "temp_low": random.randint(15, 22),
            "description": random.choice(["晴", "多云", "阴", "小雨"]),
            "icon": random.choice(["clear", "cloudy", "partly_cloudy", "rainy"])
        })
    
    return forecast