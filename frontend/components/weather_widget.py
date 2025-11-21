"""
Weather Widget - Improved Version
New Features:
1. 🌤️ Main Weather Large Display (Current Day)
2. 📅 Future Weather Small Card Display
3. Richer Weather Icons
4. Supports DeepSeek Returned Weather Data Structure
"""

import streamlit as st
from datetime import datetime, timedelta
import random


def get_weather_emoji(condition):
    """Return corresponding emoji based on weather condition"""
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
    Display Enhanced Weather Info - Main Weather Large Display, Future Weather Small Display

    Parameters:
        weather_data: Weather data dictionary, must contain:
            - temperature: Temperature
            - feels_like: Feels Like Temperature
            - weather/description: Weather Description
            - humidity: Humidity
            - wind_speed: Wind Speed
            - forecast: Future Weather Forecast Array (Optional)
        city_name: City Name (Optional)
    """

    # CSS Styles - Using Light Green
    st.markdown("""
    <style>
    /* Main Weather Card - Large Card */
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
    
    /* Future Weather Small Card */
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


    # Extract Data
    if not city_name:
        city_name = weather_data.get('city', weather_data.get('location', 'City'))

    temp = weather_data.get('temperature', 20)
    feels_like = weather_data.get('feels_like', temp)
    desc = weather_data.get('weather', weather_data.get('description', 'Clear'))
    humidity = weather_data.get('humidity', 60)
    wind_speed = weather_data.get('wind_speed', '3.0 m/s')

    # Ensure wind_speed is a string
    if not isinstance(wind_speed, str):
        wind_speed = f"{wind_speed} m/s"

    icon = get_weather_emoji(desc)

    # Generate Weather Advice
    if temp > 30:
        advice = "☀️ Hot weather, stay cool, drink plenty of water, and avoid prolonged outdoor activities."
    elif temp > 25:
        advice = "🌤️ Warm and comfortable, suitable for outings, sunscreen recommended."
    elif temp > 15:
        advice = "😊 Pleasant temperature, perfect for outdoor activities and travel."
    elif temp > 10:
        advice = "🧥 Slightly cool, bringing a jacket is recommended."
    elif temp > 0:
        advice = "🥶 Chilly, please dress warmly and wear a thick coat."
    else:
        advice = "❄️ Very cold, take precautions against the cold and stay warm."

    # Add extra advice based on weather
    desc_lower = str(desc).lower()
    if 'rain' in desc_lower or '雨' in str(desc):
        advice += " | Remember to bring an umbrella ☔"
    elif 'snow' in desc_lower or '雪' in str(desc):
        advice += " | Roads may be slippery, be careful ⚠️"
    elif 'wind' in desc_lower or '风' in str(desc) or (wind_speed and float(wind_speed.split()[0]) > 5):
        advice += " | Windy conditions, be mindful of the wind 💨"

    # ===== Main Weather Card - Large Display =====
    st.markdown(f"""
    <div class='weather-card-main'>
        <div class='weather-city-name'>📍 {city_name} · Current Weather</div>
        <div class='weather-main-display'>
            <div class='weather-icon-large'>{icon}</div>
            <div class='weather-temp-large'>{temp}°C</div>
            <div class='weather-desc-text'>{desc}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ===== Detailed Info - Using Streamlit Native Components =====
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("🌡️ Feels Like", f"{feels_like}°C")

    with col2:
        st.metric("💧 Humidity", f"{humidity}%")

    with col3:
        st.metric("💨 Wind Speed", wind_speed)

    with col4:
        air_quality = weather_data.get('air_quality', 'Good')
        st.metric("🍃 Air Quality", air_quality)

    # Travel Advice
    st.info(f"**💡 Travel Advice:** {advice}")

    st.divider()

    # ===== Future Weather Forecast - Small Card Display =====
    forecast_data = weather_data.get('forecast', [])

    if forecast_data and len(forecast_data) > 0:
        st.markdown("### 📅 Weather Forecast")
        st.caption("Weather trend for the next few days")

        # Display forecast data - using small cards
        cols = st.columns(min(len(forecast_data), 4))

        for idx, (col, day) in enumerate(zip(cols, forecast_data[:4])):
            with col:
                day_icon = get_weather_emoji(day.get('description', day.get('weather', 'Clear')))
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
        # If no forecast data, generate mock data as fallback
        st.markdown("### 📅 Weather Forecast")
        st.caption("⚠️ Forecast data temporarily unavailable, showing example data")

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

    # Extra Info (If available)
    if weather_data.get('sunrise') or weather_data.get('sunset'):
        st.divider()
        col_sun1, col_sun2 = st.columns(2)

        with col_sun1:
            if weather_data.get('sunrise'):
                st.markdown(f"🌅 **Sunrise:** {weather_data.get('sunrise')}")

        with col_sun2:
            if weather_data.get('sunset'):
                st.markdown(f"🌇 **Sunset:** {weather_data.get('sunset')}")


def get_mock_forecast_data(days=4):
    """Get mock forecast data (only used when real data is unavailable)"""
    forecast = []
    weather_options = ["Sunny", "Cloudy", "Overcast", "Light Rain", "Partly Cloudy"]

    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][date.weekday()]
        date_str = f"{date.month}/{date.day} {weekday}"

        forecast.append({
            "date": date_str,
            "temp_high": random.randint(20, 30),
            "temp_low": random.randint(15, 22),
            "description": random.choice(weather_options),
            "weather": random.choice(weather_options)
        })

    return forecast


# Testing Code
if __name__ == "__main__":
    st.set_page_config(page_title="Weather Widget Test", layout="wide")

    st.title("🌤️ Weather Widget Test - Main Weather Large Display")
    st.caption("Current Day Large Card, Future Weather Small Cards")

    # Test Data 1: Complete DeepSeek Data Format
    test_weather_deepseek = {
        'city': 'Chengdu',
        'location': 'Chengdu',
        'temperature': 18,
        'feels_like': 16,
        'weather': 'Cloudy',
        'description': 'Cloudy',
        'humidity': 70,
        'wind_speed': '2.5 m/s',
        'wind_direction': 'Southeast',
        'visibility': '12 km',
        'pressure': '1015 hPa',
        'uv_index': 3,
        'sunrise': '07:15',
        'sunset': '18:30',
        'update_time': '2025-11-21 14:30',
        'air_quality': 'Good',
        'forecast': [
            {
                'date': '11/22 Fri',
                'temp_high': 20,
                'temp_low': 14,
                'weather': 'Sunny',
                'description': 'Sunny'
            },
            {
                'date': '11/23 Sat',
                'temp_high': 22,
                'temp_low': 15,
                'weather': 'Cloudy',
                'description': 'Cloudy'
            },
            {
                'date': '11/24 Sun',
                'temp_high': 19,
                'temp_low': 13,
                'weather': 'Light Rain',
                'description': 'Light Rain'
            },
            {
                'date': '11/25 Mon',
                'temp_high': 21,
                'temp_low': 14,
                'weather': 'Partly Cloudy',
                'description': 'Partly Cloudy'
            }
        ]
    }

    st.subheader("Test 1: Complete DeepSeek Data (Main Weather + 4 Day Forecast)")
    display_weather_enhanced(test_weather_deepseek)

    st.divider()

    # Test Data 2: Different Temperature and Weather
    test_weather_hot = {
        'city': 'Sanya',
        'temperature': 32,
        'feels_like': 35,
        'weather': 'Sunny',
        'humidity': 80,
        'wind_speed': '3.5 m/s',
        'air_quality': 'Excellent',
        'forecast': [
            {'date': 'Tomorrow', 'temp_high': 33, 'temp_low': 26, 'description': 'Sunny'},
            {'date': 'Day After', 'temp_high': 34, 'temp_low': 27, 'description': 'Sunny'},
        ]
    }

    st.subheader("Test 2: Hot Weather")
    display_weather_enhanced(test_weather_hot)

    st.divider()

    # Test Data 3: Cold Weather
    test_weather_cold = {
        'city': 'Harbin',
        'temperature': -5,
        'feels_like': -8,
        'weather': 'Light Snow',
        'humidity': 65,
        'wind_speed': '5.0 m/s',
        'air_quality': 'Good',
        'forecast': [
            {'date': 'Tomorrow', 'temp_high': -3, 'temp_low': -10, 'description': 'Cloudy'},
            {'date': 'Day After', 'temp_high': -2, 'temp_low': -9, 'description': 'Sunny'},
        ]
    }

    st.subheader("Test 3: Cold Weather")
    display_weather_enhanced(test_weather_cold)