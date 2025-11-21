"""
TripPilot Chat Interface - 统一预算管理版
新功能：
1. 💰 统一预算管理(不是每个类型单独预算)
2. 📊 实时显示剩余预算
3. 🎨 使用新Logo
4. ✅ 预订成功弹窗显示扣除金额
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import json

# ==================== Import Custom Components ====================
try:
    from components.hotel_card import display_hotel_card_v2, display_hotel_list_v2
except ImportError:
    display_hotel_list_v2 = None
    display_hotel_card_v2 = None

try:
    from components.weather_widget import display_weather_enhanced
except ImportError:
    display_weather_enhanced = None

try:
    from components.flight_card import display_flight_card_v2, display_flight_list_v2
except ImportError:
    display_flight_card_v2 = None
    display_flight_list_v2 = None

# ==================== Page Configuration ====================
st.set_page_config(
    page_title="TripPilot - Intelligent Travel Assistant",
    page_icon="✈️",
    layout="wide"
)

# ==================== Initialize Session State ====================
def init_session_state():
    """Initialize all necessary session states"""
    from uuid import uuid4

    # ========== Conversation Management (统一数据结构) ==========
    if "conversations" not in st.session_state:
        default_conv_id = str(uuid4())[:8]
        st.session_state.conversations = {
            default_conv_id: {
                "id": default_conv_id,
                "name": "New Conversation",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "messages": [],
                "preferences": {
                    "destination": "",
                    "days": 3,
                    "budget": 5000,
                    "start_date": datetime.now().date(),
                    "end_date": None
                }
            }
        }
        st.session_state.current_conversation_id = default_conv_id

    # ✅ 修复旧对话数据结构(向后兼容)
    for conv_id, conv in st.session_state.conversations.items():
        if "preferences" not in conv:
            conv["preferences"] = {
                "destination": conv.get("destination", ""),
                "days": conv.get("days", 3),
                "budget": conv.get("budget", 5000),
                "start_date": conv.get("start_date", datetime.now().date()),
                "end_date": conv.get("end_date", None)
            }
        # 清理旧字段
        conv.pop("destination", None)
        conv.pop("start_date", None)
        conv.pop("end_date", None)
        conv.pop("days", None)
        conv.pop("budget", None)

    # Ensure current conversation ID is valid
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
    elif st.session_state.current_conversation_id not in st.session_state.conversations:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]

    # For backward compatibility
    current_conv = get_current_conversation()
    if current_conv:
        if "messages" not in st.session_state:
            st.session_state.messages = current_conv["messages"]
        if "current_trip" not in st.session_state:
            st.session_state.current_trip = current_conv["preferences"]

    # ✅ 统一预算管理
    if "orders" not in st.session_state:
        st.session_state.orders = []

    if "total_spent" not in st.session_state:
        st.session_state.total_spent = 0

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = st.session_state.current_conversation_id

    # ✅ 添加处理状态,避免重复处理
    if "processing" not in st.session_state:
        st.session_state.processing = False

    # ✅ 添加最后一条消息ID,避免重复触发
    if "last_message_id" not in st.session_state:
        st.session_state.last_message_id = None


# ==================== Conversation Management Functions ====================

def create_new_conversation():
    """Create a new conversation"""
    from uuid import uuid4
    new_conv_id = str(uuid4())[:8]
    st.session_state.conversations[new_conv_id] = {
        "id": new_conv_id,
        "name": f"New Conversation {len(st.session_state.conversations) + 1}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": [],
        "preferences": {
            "destination": "",
            "days": 3,
            "budget": 5000,
            "start_date": datetime.now().date(),
            "end_date": None
        }
    }
    switch_conversation(new_conv_id)
    return new_conv_id


def switch_conversation(conv_id: str):
    """Switch conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id
        # Sync messages and preferences
        current_conv = st.session_state.conversations[conv_id]
        st.session_state.messages = current_conv["messages"]
        st.session_state.current_trip = current_conv["preferences"]
        st.session_state.conversation_id = conv_id


def delete_conversation(conv_id: str):
    """Delete conversation"""
    if len(st.session_state.conversations) <= 1:
        st.error("❌ Must keep at least one conversation")
        return False

    if conv_id in st.session_state.conversations:
        del st.session_state.conversations[conv_id]

        # If deleting current conversation, switch to first one
        if st.session_state.current_conversation_id == conv_id:
            first_conv_id = list(st.session_state.conversations.keys())[0]
            switch_conversation(first_conv_id)

        return True
    return False


def rename_conversation(conv_id: str, new_name: str):
    """Rename conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["name"] = new_name
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        return True
    return False


def get_current_conversation():
    """Get current conversation"""
    conv_id = st.session_state.current_conversation_id
    return st.session_state.conversations.get(conv_id)


def update_conversation_timestamp():
    """Update current conversation timestamp"""
    conv_id = st.session_state.current_conversation_id
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


def save_message_to_conversation(role: str, content: str, **kwargs):
    """Save message to current conversation"""
    current_conv = get_current_conversation()
    if current_conv:
        message = {"role": role, "content": content, **kwargs}
        current_conv["messages"].append(message)
        st.session_state.messages = current_conv["messages"]
        update_conversation_timestamp()


# ✅ 计算剩余预算的辅助函数
def get_remaining_budget():
    """获取当前剩余预算"""
    current_conv = get_current_conversation()
    if current_conv:
        total_budget = current_conv["preferences"].get("budget", 5000)
        return total_budget - st.session_state.total_spent
    return 0


init_session_state()

# ==================== Style Definition - Light Green Theme ====================
st.markdown("""
<style>
    /* Overall Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* User Message Style - Light Green */
    .user-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 18px;
        padding: 12px 20px;
        margin: 10px 0;
        margin-left: 20%;
        box-shadow: 0 3px 15px rgba(16, 185, 129, 0.3);
        animation: fadeIn 0.3s ease-in;
    }
    
    /* AI Message Style */
    .ai-message {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 18px;
        padding: 15px 20px;
        margin: 10px 0;
        margin-right: 20%;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        line-height: 1.8;
        animation: fadeIn 0.3s ease-in;
    }
    
    /* Animation Effect */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Content Formatting */
    .ai-message h1 { color: #10b981; font-size: 1.5rem; margin: 1rem 0; }
    .ai-message h2 { color: #059669; font-size: 1.3rem; margin: 0.8rem 0; }
    .ai-message h3 { color: #047857; font-size: 1.1rem; margin: 0.6rem 0; }
    .ai-message strong { color: #047857; font-weight: 600; }
    .ai-message ul { margin: 0.5rem 0; padding-left: 1.5rem; }
    .ai-message li { margin: 0.3rem 0; line-height: 1.6; }
    
    /* Sidebar - Light Green, 1.5x Width */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6ee7b7 0%, #a7f3d0 100%);
        min-width: 350px !important;
        max-width: 500px !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 350px !important;
        max-width: 500px !important;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        width: 350px !important;
    }
    
    /* Adjust Main Content Area Left Margin */
    .main .block-container {
        padding-left: 1rem;
    }
    
    /* Sidebar Text Color for Better Readability */
    [data-testid="stSidebar"] * {
        color: #065f46 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #065f46 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #047857 !important;
        font-weight: 500 !important;
    }
    
    /* Title Area */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Sidebar Input Style */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        background-color: white !important;
        border: 1px solid #10b981 !important;
        color: #111827 !important;
    }
    
    /* Sidebar Button Style */
    [data-testid="stSidebar"] button {
        background-color: white !important;
        color: #047857 !important;
        border: 1px solid #10b981 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #10b981 !important;
        color: white !important;
    }
    
    /* Info Card */
    .info-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #10b981;
    }
    
    /* Button Style */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s;
        border: 1px solid #10b981;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
        background-color: #10b981;
        color: white;
    }
    
    /* Budget Warning Box */
    .budget-warning {
        background: #fef3c7;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #92400e;
        font-weight: 600;
    }
    
    .budget-danger {
        background: #fee2e2;
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #991b1b;
        font-weight: 600;
    }
    
    .budget-ok {
        background: #d1fae5;
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #065f46;
        font-weight: 600;
    }
    
    /* Sidebar Expander Style */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid #10b981 !important;
        border-radius: 8px !important;
        color: #047857 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid #a7f3d0 !important;
        border-top: none !important;
    }
    
    /* Primary Button Style */
    .stButton>button[kind="primary"] {
        background-color: #10b981;
        color: white;
    }
    
    .stButton>button[kind="primary"]:hover {
        background-color: #059669;
    }
    
    /* Sidebar Metric Style */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #10b981;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #047857 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #065f46 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API Interaction Functions ====================
def call_backend_api(message: str) -> dict:
    """Call backend API to get response - Optimized version"""
    try:
        trip = st.session_state.current_trip

        request_data = {
            "prompt": message,
            "preferences": {
                "budget": max(500, trip.get("budget", 5000)),
                "destination": trip.get("destination", ""),
                "days": max(1, trip.get("days", 3)),
                "start_date": str(trip.get("start_date", datetime.now().date())),
                "end_date": str(trip.get("end_date", ""))
            },
            "conversation_history": st.session_state.messages[-10:] if st.session_state.messages else []
        }

        response = requests.post(
            "http://localhost:5000/api/chat",
            json=request_data,
            timeout=90
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "action": "error",
                "content": f"Sorry, server returned error (Status code: {response.status_code})",
                "data": None,
                "suggestions": []
            }

    except requests.exceptions.Timeout:
        return {
            "action": "error",
            "content": "Sorry, request timed out. Please try again later.",
            "data": None,
            "suggestions": ["Resend message"]
        }
    except requests.exceptions.ConnectionError:
        return {
            "action": "error",
            "content": "Cannot connect to backend service. Please ensure the backend is running.",
            "data": None,
            "suggestions": ["Check backend service", "Try again"]
        }
    except Exception as e:
        return {
            "action": "error",
            "content": f"An error occurred: {str(e)}",
            "data": None,
            "suggestions": []
        }


# ==================== Message Display Functions ====================
def display_user_message(content: str):
    """Display user message"""
    st.markdown(f"""
    <div class="user-message">
        <strong>👤 You</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def display_ai_message(message: dict, msg_idx: int = 0):
    """Display AI message"""
    content = message.get("content", "")
    action = message.get("action", "")
    data = message.get("data", None)
    suggestions = message.get("suggestions", [])

    # AI message container
    st.markdown(f"""
    <div class="ai-message">
        <strong>🤖 AI Assistant</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)

    # Display data cards
    if data:
        if action == "search_hotels" and isinstance(data, list):
            display_hotels(data, msg_idx)
        elif action == "search_flights" and isinstance(data, list):
            display_flights(data, msg_idx)
        elif action == "weather" and isinstance(data, dict):
            display_weather(data)

    # Display suggestions
    if suggestions:
        display_suggestions(suggestions, msg_idx)


def display_hotels(hotels: list, msg_idx: int):
    """Display hotel list with unified budget"""
    if display_hotel_list_v2:
        # ✅ 传递预算信息和预订回调
        display_hotel_list_v2(
            hotels,
            message_id=msg_idx,
            on_book_callback=lambda hotel, price: handle_booking("hotel", hotel, price)
        )
    else:
        _display_hotels_fallback(hotels, msg_idx)


def _display_hotels_fallback(hotels: list, msg_idx: int):
    """Hotel fallback display"""
    st.subheader("🏨 Recommended Hotels")

    remaining = get_remaining_budget()
    st.info(f"💰 剩余预算: ¥{remaining:,.0f}")

    for idx, hotel in enumerate(hotels):
        price = hotel.get('price', 0)
        with st.expander(f"⭐ {hotel.get('name', 'Unknown')} - ¥{price}/night", expanded=idx == 0):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Location:** {hotel.get('location', 'N/A')}")
                st.write(f"**Address:** {hotel.get('address', 'N/A')}")
                st.write(f"**Rating:** {'⭐' * int(hotel.get('rating', 0))}")
                st.write(f"**Amenities:** {', '.join(hotel.get('amenities', []))}")
            with col2:
                st.metric("Price", f"¥{price}/night")

                # ✅ 检查预算
                if price > remaining:
                    st.error("💰 预算不足")
                else:
                    if st.button(f"Book", key=f"book_hotel_{msg_idx}_{idx}"):
                        handle_booking("hotel", hotel, price)


def display_flights(flights: list, msg_idx: int):
    """Display flight list with unified budget"""
    if display_flight_list_v2:
        # ✅ 传递消息ID
        display_flight_list_v2(flights, message_id=msg_idx)
    else:
        _display_flights_fallback(flights, msg_idx)


def _display_flights_fallback(flights: list, msg_idx: int):
    """Flight fallback display"""
    st.subheader("✈️ Recommended Flights")

    remaining = get_remaining_budget()
    st.info(f"💰 剩余预算: ¥{remaining:,.0f}")

    for idx, flight in enumerate(flights):
        price = flight.get('price', 0)
        with st.expander(
            f"{flight.get('carrier_name', 'Unknown')} {flight.get('flight_number', '')} - ¥{price}",
            expanded=idx == 0
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Departure:** {flight.get('departure_time', '')}")
                st.write(f"**Origin:** {flight.get('origin', 'N/A')}")
            with col2:
                st.write(f"**Arrival:** {flight.get('arrival_time', '')}")
                st.write(f"**Destination:** {flight.get('destination', 'N/A')}")
            with col3:
                st.write(f"**Duration:** {flight.get('duration', 'N/A')}")
                st.write(f"**Class:** {flight.get('cabin_class', 'N/A')}")

            # ✅ 检查预算
            if price > remaining:
                st.error("💰 预算不足")
            else:
                if st.button(f"Book", key=f"book_flight_{msg_idx}_{idx}"):
                    handle_booking("flight", flight, price)


def display_weather(weather: dict):
    """Display weather information"""
    if display_weather_enhanced:
        formatted_weather = {
            "location": weather.get("location", weather.get("city", "")),
            "temperature": weather.get("temperature", 0),
            "feels_like": weather.get("feels_like", 0),
            "weather": weather.get("weather", ""),
            "description": weather.get("description", ""),
            "humidity": weather.get("humidity", 0),
            "wind_speed": weather.get("wind_speed", ""),
            "wind_direction": weather.get("wind_direction", ""),
            "visibility": weather.get("visibility", ""),
            "pressure": weather.get("pressure", ""),
            "uv_index": weather.get("uv_index", 0),
            "sunrise": weather.get("sunrise", ""),
            "sunset": weather.get("sunset", ""),
            "update_time": weather.get("update_time", ""),
            "forecast": weather.get("forecast", [])
        }
        display_weather_enhanced(formatted_weather)
    else:
        _display_weather_fallback(weather)


def _display_weather_fallback(weather: dict):
    """Weather fallback display"""
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Temperature", f"{weather.get('temperature', 'N/A')}°C")
        with col2:
            st.metric("Humidity", f"{weather.get('humidity', 'N/A')}%")
        with col3:
            st.metric("Wind Speed", weather.get('wind_speed', 'N/A'))
        with col4:
            st.metric("Weather", weather.get('weather', 'N/A'))


# ==================== Suggestion Buttons ====================
def display_suggestions(suggestions: list, msg_idx: int = 0):
    """Display suggestion buttons"""
    if not suggestions:
        return

    st.markdown("**You might also want to know:**")
    cols = st.columns(min(len(suggestions[:3]), 3))
    for idx, (col, suggestion) in enumerate(zip(cols, suggestions[:3])):
        with col:
            button_key = f"sug_{msg_idx}_{idx}_{suggestion[:20]}"
            if st.button(f"{suggestion}", key=button_key):
                st.session_state.pending_message = suggestion


# ✅ 统一的预订处理函数
def handle_booking(order_type: str, item: dict, price: float):
    """
    统一的预订处理函数 - 检查预算并扣除

    Args:
        order_type: 订单类型 (hotel/flight)
        item: 订单项目数据
        price: 价格
    """
    remaining = get_remaining_budget()

    # 检查预算是否足够
    if price > remaining:
        st.error(f"❌ 预算不足! 需要 ¥{price:,.0f}, 剩余 ¥{remaining:,.0f}")
        return False

    # 添加订单
    order = {
        "type": order_type,
        "item": item,
        "price": price,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.orders.append(order)

    # ✅ 扣除预算
    st.session_state.total_spent += price
    new_remaining = get_remaining_budget()

    # ✅ 显示成功消息和弹窗
    success_msg = f"""
    ✅ **预订成功!**
    
    - 类型: {'🏨 酒店' if order_type == 'hotel' else '✈️ 航班'}
    - 项目: {item.get('name', item.get('carrier_name', 'Unknown'))}
    - 扣除金额: ¥{price:,.0f}
    - 剩余预算: ¥{new_remaining:,.0f}
    """

    st.success(success_msg)
    st.balloons()

    # 预算警告
    if new_remaining < 0:
        st.error(f"⚠️ 预算超支 ¥{abs(new_remaining):,.0f}!")
    elif new_remaining < 500:
        st.warning(f"⚠️ 预算即将用完,剩余 ¥{new_remaining:,.0f}")

    return True


# ==================== Main Function ====================
def handle_user_input(message: str):
    """Handle user input"""
    if not message.strip():
        return

    if st.session_state.processing:
        return

    st.session_state.processing = True

    try:
        save_message_to_conversation("user", message)

        status_placeholder = st.empty()
        status_placeholder.info("🤔 AI is thinking, please wait...")

        response = call_backend_api(message)
        status_placeholder.empty()

        save_message_to_conversation(
            "assistant",
            response.get("content", ""),
            action=response.get("action"),
            data=response.get("data"),
            suggestions=response.get("suggestions", [])
        )

    finally:
        st.session_state.processing = False
        st.rerun()


# ==================== Sidebar ====================
with st.sidebar:
    st.header("💬 Conversation Management")

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("➕ New Conversation", use_container_width=True, type="primary", key="new_conv_btn"):
            create_new_conversation()
            st.rerun()

    with col2:
        if st.button("🔄", use_container_width=True, help="Refresh", key="refresh_btn"):
            st.rerun()

    st.divider()

    # ✅ 实时预算显示 - 放在最显眼的位置
    st.markdown("### 💰 预算管理")

    current_conv = get_current_conversation()
    if current_conv:
        total_budget = current_conv["preferences"].get("budget", 5000)
        remaining = get_remaining_budget()
        usage_percent = (st.session_state.total_spent / total_budget * 100) if total_budget > 0 else 0

        # 预算进度条
        st.progress(min(usage_percent / 100, 1.0))

        # 预算指标
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.metric(
                "总预算",
                f"¥{total_budget:,.0f}",
                delta=None
            )
        with col_b2:
            st.metric(
                "剩余",
                f"¥{remaining:,.0f}",
                delta=f"-¥{st.session_state.total_spent:,.0f}" if st.session_state.total_spent > 0 else None,
                delta_color="inverse"
            )

        # 预算状态提示
        if remaining < 0:
            st.markdown(f"""
            <div class="budget-danger">
                ⚠️ 预算超支 ¥{abs(remaining):,.0f}
            </div>
            """, unsafe_allow_html=True)
        elif remaining < total_budget * 0.2:
            st.markdown(f"""
            <div class="budget-warning">
                ⚠️ 预算即将用完 ({usage_percent:.1f}% 已使用)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="budget-ok">
                ✅ 预算充足 ({usage_percent:.1f}% 已使用)
            </div>
            """, unsafe_allow_html=True)

        st.caption(f"已花费: ¥{st.session_state.total_spent:,.0f} | 订单数: {len(st.session_state.orders)}")

    st.divider()

    # Conversation list
    st.markdown("#### 📋 Conversation List")

    sorted_convs = sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1]["updated_at"],
        reverse=True
    )

    for conv_id, conv in sorted_convs:
        is_active = conv_id == st.session_state.current_conversation_id
        msg_count = len(conv["messages"])

        with st.expander(
            f"{'🟢' if is_active else '⚪'} {conv['name']} ({msg_count} msgs)",
            expanded=is_active
        ):
            st.caption(f"Created: {conv['created_at']}")
            st.caption(f"Updated: {conv['updated_at']}")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if not is_active:
                    if st.button("Switch", key=f"switch_{conv_id}", use_container_width=True):
                        switch_conversation(conv_id)
                        st.rerun()

            with col_b:
                if st.button("Rename", key=f"rename_{conv_id}", use_container_width=True):
                    st.session_state[f"renaming_{conv_id}"] = True
                    st.rerun()

            with col_c:
                if len(st.session_state.conversations) > 1:
                    if st.button("Delete", key=f"delete_{conv_id}", use_container_width=True):
                        if delete_conversation(conv_id):
                            st.success("✅ Deleted")
                            st.rerun()

            if st.session_state.get(f"renaming_{conv_id}", False):
                new_name = st.text_input(
                    "New Name",
                    value=conv['name'],
                    key=f"new_name_{conv_id}"
                )
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("Confirm", key=f"confirm_{conv_id}", use_container_width=True):
                        if new_name.strip():
                            rename_conversation(conv_id, new_name.strip())
                            st.session_state[f"renaming_{conv_id}"] = False
                            st.rerun()
                with col_y:
                    if st.button("Cancel", key=f"cancel_{conv_id}", use_container_width=True):
                        st.session_state[f"renaming_{conv_id}"] = False
                        st.rerun()

    st.divider()

    # Current conversation settings
    st.markdown("#### ⚙️ Current Settings")

    current_conv = get_current_conversation()
    if current_conv:
        preferences = current_conv["preferences"]

        destination = st.text_input(
            "Destination",
            value=preferences.get("destination", ""),
            placeholder="e.g.: Chengdu, Hangzhou, Tokyo",
            key="sidebar_destination"
        )
        preferences["destination"] = destination

        col1, col2 = st.columns(2)
        with col1:
            days = st.number_input(
                "Days",
                min_value=1,
                max_value=30,
                value=max(1, preferences.get("days", 3)),
                step=1,
                key="sidebar_days"
            )
            preferences["days"] = days

        with col2:
            budget = st.number_input(
                "Budget (¥)",
                min_value=500,
                max_value=100000,
                value=max(500, int(preferences.get("budget", 5000))),
                step=500,
                key="sidebar_budget"
            )
            preferences["budget"] = budget

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=preferences.get("start_date", datetime.now().date()),
                min_value=datetime.now().date(),
                key="sidebar_start_date"
            )
            preferences["start_date"] = start_date

        with col2:
            default_end = start_date + timedelta(days=days-1)
            end_date = st.date_input(
                "End Date",
                value=default_end,
                min_value=start_date,
                key="sidebar_end_date"
            )
            preferences["end_date"] = end_date

        st.session_state.current_trip = preferences

    st.divider()

    st.subheader("Quick Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Current", use_container_width=True, key="clear_btn"):
            current_conv = get_current_conversation()
            if current_conv:
                current_conv["messages"] = []
                st.session_state.messages = []
                st.success("Cleared")
                st.rerun()

    with col2:
        if st.button("View Orders", use_container_width=True, key="view_orders_btn"):
            if st.session_state.orders:
                st.info(f"Total {len(st.session_state.orders)} orders")
            else:
                st.info("No orders yet")

    if st.session_state.orders:
        with st.expander(f"Order Details ({len(st.session_state.orders)})", expanded=False):
            for idx, order in enumerate(st.session_state.orders, 1):
                item = order['item']
                order_type = order['type']
                name = item.get('name', item.get('carrier_name', 'Unknown'))
                price = order.get('price', 0)

                st.write(f"**{idx}. {name}**")
                st.caption(f"Type: {order_type} | Price: ¥{price:,.0f}")
                if st.button("Delete", key=f"del_order_{idx}"):
                    st.session_state.total_spent -= price
                    st.session_state.orders.pop(idx-1)
                    st.rerun()
                if idx < len(st.session_state.orders):
                    st.divider()

    st.divider()

    # Status info
    current_conv = get_current_conversation()
    if current_conv:
        st.caption(f"""
        **Current Status**
        - Conversation: {current_conv['name']}
        - Messages: {len(current_conv['messages'])}
        - Destination: {current_conv['preferences'].get('destination') or 'Not set'}
        - Budget: ¥{current_conv['preferences'].get('budget', 0):,}
        - Spent: ¥{st.session_state.total_spent:,}
        - Days: {current_conv['preferences'].get('days', 0)}
        """)

    st.divider()

    # Backend status
    try:
        response = requests.get("http://localhost:5000/health", timeout=1)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Not Started")
        st.caption("Run: `python app.py`")


# ==================== Main Interface ====================
st.title("✈️ TripPilot Intelligent Travel Assistant")
st.caption("Based on DeepSeek AI | Make Travel Planning Simple and Fun")

# Display budget at top
current_conv = get_current_conversation()
if current_conv:
    total_budget = current_conv["preferences"].get("budget", 5000)
    remaining = get_remaining_budget()

    col_top1, col_top2, col_top3 = st.columns([2, 1, 1])
    with col_top1:
        st.info(f"📝 Current: **{current_conv['name']}** | {len(current_conv['messages'])} messages")
    with col_top2:
        st.metric("💰 Total Budget", f"¥{total_budget:,.0f}")
    with col_top3:
        delta_color = "normal" if remaining >= 0 else "inverse"
        st.metric("Remaining", f"¥{remaining:,.0f}", delta_color=delta_color)

if not st.session_state.messages:
    st.markdown("""
    <div class="info-card">
    <h3>Hello! I'm your dedicated AI travel assistant</h3>
    <p>I can provide you with personalized travel services, including itinerary planning, hotel recommendations, flight inquiries, and more.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **Itinerary Planning**
        - Detailed daily arrangements
        - Attraction route optimization
        - Time allocation suggestions
        """)

    with col2:
        st.markdown("""
        **Accommodation Recommendations**
        - Various hotel grade options
        - Location advantage analysis
        - Value-for-money ranking
        """)

    with col3:
        st.markdown("""
        **Transportation Arrangement**
        - Flight schedule inquiry
        - Optimal route recommendations
        - Transportation tool suggestions
        """)

    st.divider()

    st.subheader("Quick Start - Click to Try")

    example_queries = [
        "Help me plan a 3-day trip to Chengdu with a budget of 5000 yuan",
        "Recommend hotels near West Lake in Hangzhou",
        "Query flights from Beijing to Shanghai",
        "What are the must-see attractions in Tokyo?",
        "What's the weather like in Sanya, what clothes should I bring?"
    ]

    cols = st.columns(2)
    for idx, query in enumerate(example_queries):
        with cols[idx % 2]:
            if st.button(f"{query}", key=f"example_query_{idx}", use_container_width=True):
                st.session_state.pending_message = query

    st.divider()

    st.info("**Tip**: You can directly tell me your travel needs in the input box below!")

# Display message history
message_container = st.container()
with message_container:
    for msg_idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            display_user_message(message["content"])
        else:
            display_ai_message(message, msg_idx)

# Handle pending message
if "pending_message" in st.session_state and st.session_state.pending_message:
    pending_msg = st.session_state.pending_message
    st.session_state.pending_message = None
    handle_user_input(pending_msg)

# Input box
user_input = st.chat_input(
    "Tell me your travel needs...",
    key="chat_input"
)

if user_input:
    handle_user_input(user_input)

# Footer
with st.container():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("✈️ TripPilot v2.1 - Your Intelligent Travel Partner")

    with col2:
        if st.session_state.messages:
            last_msg_time = datetime.now().strftime("%H:%M")
            st.caption(f"Last updated: {last_msg_time}")

    with col3:
        st.caption("💡 Tip: Unified budget management across all bookings")