"""
TripPilot 聊天界面 - 增强版
新增功能:
1. 对话管理（新建、切换、重命名、删除）
2. 优化性能，减少卡顿
3. 改进的消息处理流程
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import json

# ==================== 导入自定义组件 ====================
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

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="TripPilot - 智能旅行助手",
    page_icon="💬",
    layout="wide"
)

# ==================== 初始化会话状态 ====================
def init_session_state():
    """初始化所有必要的会话状态"""
    from uuid import uuid4

    # ========== 对话管理 ==========
    if "conversations" not in st.session_state:
        default_conv_id = str(uuid4())[:8]
        st.session_state.conversations = {
            default_conv_id: {
                "id": default_conv_id,
                "name": "新对话",
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

    # 确保当前对话ID有效
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
    elif st.session_state.current_conversation_id not in st.session_state.conversations:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]

    # 为兼容性保留旧的变量
    current_conv = get_current_conversation()
    if "messages" not in st.session_state:
        st.session_state.messages = current_conv["messages"]
    if "current_trip" not in st.session_state:
        st.session_state.current_trip = current_conv["preferences"]

    if "orders" not in st.session_state:
        st.session_state.orders = []

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = st.session_state.current_conversation_id

# ==================== 对话管理函数 ====================

def create_new_conversation():
    """创建新对话"""
    from uuid import uuid4
    new_conv_id = str(uuid4())[:8]
    st.session_state.conversations[new_conv_id] = {
        "id": new_conv_id,
        "name": f"新对话 {len(st.session_state.conversations) + 1}",
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
    """切换对话"""
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id
        # 同步消息和偏好设置
        current_conv = st.session_state.conversations[conv_id]
        st.session_state.messages = current_conv["messages"]
        st.session_state.current_trip = current_conv["preferences"]
        st.session_state.conversation_id = conv_id


def delete_conversation(conv_id: str):
    """删除对话"""
    if len(st.session_state.conversations) <= 1:
        st.error("❌ 至少需要保留一个对话")
        return False

    if conv_id in st.session_state.conversations:
        del st.session_state.conversations[conv_id]

        # 如果删除的是当前对话，切换到第一个对话
        if st.session_state.current_conversation_id == conv_id:
            first_conv_id = list(st.session_state.conversations.keys())[0]
            switch_conversation(first_conv_id)

        return True
    return False


def rename_conversation(conv_id: str, new_name: str):
    """重命名对话"""
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["name"] = new_name
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        return True
    return False


def get_current_conversation():
    """获取当前对话"""
    conv_id = st.session_state.current_conversation_id
    return st.session_state.conversations.get(conv_id)


def update_conversation_timestamp():
    """更新当前对话的时间戳"""
    conv_id = st.session_state.current_conversation_id
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


def save_message_to_conversation(role: str, content: str, **kwargs):
    """将消息保存到当前对话"""
    current_conv = get_current_conversation()
    if current_conv:
        message = {"role": role, "content": content, **kwargs}
        current_conv["messages"].append(message)
        st.session_state.messages = current_conv["messages"]
        update_conversation_timestamp()


init_session_state()

# ==================== 样式定义 - 浅绿色主题 ====================
st.markdown("""
<style>
    /* 整体背景 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 用户消息样式 - 浅绿色 */
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
    
    /* AI消息样式 */
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
    
    /* 动画效果 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* 内容格式化 */
    .ai-message h1 { color: #10b981; font-size: 1.5rem; margin: 1rem 0; }
    .ai-message h2 { color: #059669; font-size: 1.3rem; margin: 0.8rem 0; }
    .ai-message h3 { color: #047857; font-size: 1.1rem; margin: 0.6rem 0; }
    .ai-message strong { color: #047857; font-weight: 600; }
    .ai-message ul { margin: 0.5rem 0; padding-left: 1.5rem; }
    .ai-message li { margin: 0.3rem 0; line-height: 1.6; }
    
    /* 侧边栏 - 浅绿色，宽度1.5倍 */
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
    
    /* 调整主内容区域的左边距 */
    .main .block-container {
        padding-left: 1rem;
    }
    
    /* 侧边栏文字颜色增强可读性 */
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
    
    /* 标题区域 */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* 侧边栏输入框样式 */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        background-color: white !important;
        border: 1px solid #10b981 !important;
        color: #111827 !important;
    }
    
    /* 侧边栏按钮样式 */
    [data-testid="stSidebar"] button {
        background-color: white !important;
        color: #047857 !important;
        border: 1px solid #10b981 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #10b981 !important;
        color: white !important;
    }
    
    /* 信息卡片 */
    .info-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #10b981;
    }
    
    /* 按钮样式 */
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
    
    /* 侧边栏expander样式 */
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
    
    /* 主要按钮样式 */
    .stButton>button[kind="primary"] {
        background-color: #10b981;
        color: white;
    }
    
    .stButton>button[kind="primary"]:hover {
        background-color: #059669;
    }
    
    /* 侧边栏metric样式 */
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
    
    /* 侧边栏成功/信息/错误消息 */
    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stInfo,
    [data-testid="stSidebar"] .stError {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }
    
    /* 对话列表项样式 */
    .conversation-item {
        padding: 12px;
        margin: 5px 0;
        border-radius: 8px;
        background-color: rgba(255, 255, 255, 0.8);
        border: 1px solid #10b981;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .conversation-item:hover {
        background-color: rgba(255, 255, 255, 1);
        transform: translateX(3px);
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    .conversation-item.active {
        background-color: #10b981 !important;
        color: white !important;
        border-color: #059669 !important;
    }
    
    .conversation-item.active * {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API交互函数 ====================
def call_backend_api(message: str) -> dict:
    """调用后端API获取回复 - 优化版"""
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
                "content": f"抱歉，服务器返回错误 (状态码: {response.status_code})",
                "data": None,
                "suggestions": []
            }

    except requests.exceptions.Timeout:
        return {
            "action": "error",
            "content": "抱歉，请求超时。请稍后再试。",
            "data": None,
            "suggestions": ["重新发送消息"]
        }
    except requests.exceptions.ConnectionError:
        return {
            "action": "error",
            "content": "无法连接到后端服务，请确保后端正在运行。",
            "data": None,
            "suggestions": ["检查后端服务", "重新尝试"]
        }
    except Exception as e:
        return {
            "action": "error",
            "content": f"发生错误: {str(e)}",
            "data": None,
            "suggestions": []
        }


# ==================== 消息显示函数 ====================
def display_user_message(content: str):
    """显示用户消息"""
    st.markdown(f"""
    <div class="user-message">
        <strong>👤 您</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def display_ai_message(message: dict, msg_idx: int = 0):
    """显示AI消息"""
    content = message.get("content", "")
    action = message.get("action", "")
    data = message.get("data", None)
    suggestions = message.get("suggestions", [])

    # AI消息容器
    st.markdown(f"""
    <div class="ai-message">
        <strong>🤖 AI助手</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)

    # 显示数据卡片
    if data:
        if action == "search_hotels" and isinstance(data, list):
            display_hotels(data, msg_idx)
        elif action == "search_flights" and isinstance(data, list):
            display_flights(data, msg_idx)
        elif action == "weather" and isinstance(data, dict):
            display_weather(data)

    # 显示建议
    if suggestions:
        display_suggestions(suggestions, msg_idx)


def display_hotels(hotels: list, msg_idx: int):
    """显示酒店列表"""
    if display_hotel_list_v2:
        display_hotel_list_v2(hotels)
    else:
        _display_hotels_fallback(hotels, msg_idx)


def _display_hotels_fallback(hotels: list, msg_idx: int):
    """酒店备用显示"""
    st.subheader("🏨 推荐酒店")
    for idx, hotel in enumerate(hotels):
        with st.expander(f"⭐ {hotel.get('name', 'Unknown')} - ¥{hotel.get('price', 0)}/晚", expanded=idx == 0):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**位置:** {hotel.get('location', 'N/A')}")
                st.write(f"**地址:** {hotel.get('address', 'N/A')}")
                st.write(f"**评分:** {'⭐' * int(hotel.get('rating', 0))}")
                st.write(f"**设施:** {', '.join(hotel.get('amenities', []))}")
            with col2:
                st.metric("价格", f"¥{hotel.get('price', 0)}/晚")
                if st.button(f"预订", key=f"book_hotel_{msg_idx}_{idx}"):
                    add_to_orders("hotel", hotel)


def display_flights(flights: list, msg_idx: int):
    """显示航班列表"""
    if display_flight_list_v2:
        display_flight_list_v2(flights)
    else:
        _display_flights_fallback(flights, msg_idx)


def _display_flights_fallback(flights: list, msg_idx: int):
    """航班备用显示"""
    st.subheader("✈️ 推荐航班")
    for idx, flight in enumerate(flights):
        with st.expander(
            f"{flight.get('carrier_name', 'Unknown')} {flight.get('flight_number', '')} - ¥{flight.get('price', 0)}",
            expanded=idx == 0
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**出发:** {flight.get('departure_time', '')}")
                st.write(f"**起飞地:** {flight.get('origin', 'N/A')}")
            with col2:
                st.write(f"**到达:** {flight.get('arrival_time', '')}")
                st.write(f"**目的地:** {flight.get('destination', 'N/A')}")
            with col3:
                st.write(f"**时长:** {flight.get('duration', 'N/A')}")
                st.write(f"**舱位:** {flight.get('cabin_class', 'N/A')}")

            if st.button(f"预订", key=f"book_flight_{msg_idx}_{idx}"):
                add_to_orders("flight", flight)


def display_weather(weather: dict):
    """显示天气信息"""
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
    """天气备用展示"""
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("温度", f"{weather.get('temperature', 'N/A')}°C")
        with col2:
            st.metric("湿度", f"{weather.get('humidity', 'N/A')}%")
        with col3:
            st.metric("风速", weather.get('wind_speed', 'N/A'))
        with col4:
            st.metric("天气", weather.get('weather', 'N/A'))


# ==================== 建议按钮 ====================
def display_suggestions(suggestions: list, msg_idx: int = 0):
    """显示建议按钮"""
    if not suggestions:
        return

    st.markdown("**您可能还想了解：**")
    cols = st.columns(min(len(suggestions[:3]), 3))
    for idx, (col, suggestion) in enumerate(zip(cols, suggestions[:3])):
        with col:
            if st.button(f"{suggestion}", key=f"sug_{msg_idx}_{idx}_{hash(suggestion)}"):
                handle_user_input(suggestion)


def add_to_orders(order_type: str, item: dict):
    """添加到订单"""
    order = {
        "type": order_type,
        "item": item,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.orders.append(order)
    st.success(f"已添加到订单！共 {len(st.session_state.orders)} 个订单")
    st.balloons()


# ==================== 主函数 - 优化版 ====================
def handle_user_input(message: str):
    """处理用户输入 - 优化版，减少卡顿"""
    if not message.strip():
        return

    # 立即添加用户消息并更新UI（不rerun）
    save_message_to_conversation("user", message)

    # 使用 st.empty() 创建占位符来动态更新内容
    # 这样可以避免全页面重载
    with st.spinner("🤔 AI正在思考，请稍候..."):
        response = call_backend_api(message)

    # 添加AI响应
    save_message_to_conversation("assistant", response.get("content", ""),
                                 action=response.get("action"),
                                 data=response.get("data"),
                                 suggestions=response.get("suggestions", []))

    # 只在添加消息后rerun一次
    st.rerun()


# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("💬 对话管理")

    # 新建对话按钮
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("➕ 新建对话", use_container_width=True, type="primary"):
            create_new_conversation()
            st.rerun()

    with col2:
        # 刷新按钮
        if st.button("🔄", use_container_width=True, help="刷新对话列表"):
            st.rerun()

    st.divider()

    # 对话列表
    st.markdown("#### 📋 对话列表")

    # 按更新时间排序对话
    sorted_convs = sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1]["updated_at"],
        reverse=True
    )

    # 显示对话列表
    for conv_id, conv in sorted_convs:
        is_active = conv_id == st.session_state.current_conversation_id
        msg_count = len(conv["messages"])

        # 使用expander来显示每个对话
        with st.expander(
            f"{'🟢' if is_active else '⚪'} {conv['name']} ({msg_count}条)",
            expanded=is_active
        ):
            st.caption(f"创建于: {conv['created_at']}")
            st.caption(f"更新于: {conv['updated_at']}")

            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if not is_active:
                    if st.button("切换", key=f"switch_{conv_id}", use_container_width=True):
                        switch_conversation(conv_id)
                        st.rerun()

            with col_b:
                if st.button("重命名", key=f"rename_{conv_id}", use_container_width=True):
                    st.session_state[f"renaming_{conv_id}"] = True
                    st.rerun()

            with col_c:
                if len(st.session_state.conversations) > 1:
                    if st.button("删除", key=f"delete_{conv_id}", use_container_width=True):
                        if delete_conversation(conv_id):
                            st.success("✅ 已删除")
                            st.rerun()

            # 重命名输入框
            if st.session_state.get(f"renaming_{conv_id}", False):
                new_name = st.text_input(
                    "新名称",
                    value=conv['name'],
                    key=f"new_name_{conv_id}"
                )
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("确认", key=f"confirm_{conv_id}", use_container_width=True):
                        if new_name.strip():
                            rename_conversation(conv_id, new_name.strip())
                            st.session_state[f"renaming_{conv_id}"] = False
                            st.rerun()
                with col_y:
                    if st.button("取消", key=f"cancel_{conv_id}", use_container_width=True):
                        st.session_state[f"renaming_{conv_id}"] = False
                        st.rerun()

    st.divider()

    # 当前对话设置
    st.markdown("#### ⚙️ 当前对话设置")

    current_conv = get_current_conversation()
    if current_conv:
        preferences = current_conv["preferences"]

        destination = st.text_input(
            "目的地",
            value=preferences.get("destination", ""),
            placeholder="例如：成都、杭州、东京",
            help="输入您想去的城市或地区",
            key="sidebar_destination"
        )
        preferences["destination"] = destination

        col1, col2 = st.columns(2)
        with col1:
            days = st.number_input(
                "天数",
                min_value=1,
                max_value=30,
                value=max(1, preferences.get("days", 3)),
                step=1,
                help="旅行天数（1-30天）",
                key="sidebar_days"
            )
            preferences["days"] = days

        with col2:
            budget = st.number_input(
                "预算 (¥)",
                min_value=500,
                max_value=100000,
                value=max(500, int(preferences.get("budget", 5000))),
                step=500,
                help="总预算金额",
                key="sidebar_budget"
            )
            preferences["budget"] = budget

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "开始日期",
                value=preferences.get("start_date", datetime.now().date()),
                min_value=datetime.now().date(),
                help="旅行开始日期",
                key="sidebar_start_date"
            )
            preferences["start_date"] = start_date

        with col2:
            default_end = start_date + timedelta(days=days-1)
            end_date = st.date_input(
                "结束日期",
                value=default_end,
                min_value=start_date,
                help="旅行结束日期",
                key="sidebar_end_date"
            )
            preferences["end_date"] = end_date

        # 保存到current_trip以保持兼容性
        st.session_state.current_trip = preferences

    st.divider()

    st.subheader("快速操作")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("清空当前对话", use_container_width=True):
            current_conv = get_current_conversation()
            if current_conv:
                current_conv["messages"] = []
                st.session_state.messages = []
                st.success("对话已清空")
                st.rerun()

    with col2:
        if st.button("查看订单", use_container_width=True):
            if st.session_state.orders:
                st.info(f"共 {len(st.session_state.orders)} 个订单")
            else:
                st.info("暂无订单")

    if st.session_state.orders:
        with st.expander(f"订单详情 ({len(st.session_state.orders)})", expanded=False):
            for idx, order in enumerate(st.session_state.orders, 1):
                item = order['item']
                order_type = order['type']
                name = item.get('name', 'Unknown')
                price = item.get('price', 0) if order_type == 'hotel' else item.get('total_price', 0)

                st.write(f"**{idx}. {name}**")
                st.caption(f"类型: {order_type} | 价格: ¥{price}")
                if st.button("删除", key=f"del_order_{idx}"):
                    st.session_state.orders.pop(idx-1)
                    st.rerun()
                if idx < len(st.session_state.orders):
                    st.divider()

    st.divider()

    # 状态信息
    current_conv = get_current_conversation()
    if current_conv:
        st.caption(f"""
        **当前对话状态**
        - 对话名: {current_conv['name']}
        - 消息数: {len(current_conv['messages'])}
        - 目的地: {current_conv['preferences'].get('destination') or '未设置'}
        - 预算: ¥{current_conv['preferences'].get('budget', 0):,}
        - 天数: {current_conv['preferences'].get('days', 0)}天
        """)

    st.divider()

    # 后端状态
    try:
        response = requests.get("http://localhost:5000/health", timeout=1)
        if response.status_code == 200:
            st.success("✅ 后端已连接")
        else:
            st.error("❌ 后端异常")
    except:
        st.error("❌ 后端未启动")
        st.caption("运行: `python app.py`")


# ==================== 主界面 ====================
st.title("💬 TripPilot 智能旅行助手")
st.caption("基于 DeepSeek AI | 让旅行规划变得简单有趣")

# 显示当前对话名称
current_conv = get_current_conversation()
if current_conv:
    st.info(f"📝 当前对话: **{current_conv['name']}** | {len(current_conv['messages'])}条消息")

if not st.session_state.messages:
    st.markdown("""
    <div class="info-card">
    <h3>您好！我是您的专属AI旅行助手</h3>
    <p>我可以为您提供个性化的旅行服务，包括行程规划、酒店推荐、航班查询等。</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **行程规划**
        - 详细的每日安排
        - 景点路线优化
        - 时间分配建议
        """)

    with col2:
        st.markdown("""
        **住宿推荐**
        - 各档次酒店选择
        - 位置优势分析
        - 性价比排序
        """)

    with col3:
        st.markdown("""
        **交通安排**
        - 航班时刻查询
        - 最优路线推荐
        - 交通工具建议
        """)

    st.divider()

    st.subheader("快速开始 - 点击试试")

    example_queries = [
        "帮我规划一个成都3日游，预算5000元",
        "推荐杭州西湖附近的酒店",
        "查询北京到上海的航班",
        "东京有什么必去的景点？",
        "三亚的天气怎么样，需要带什么衣服？"
    ]

    cols = st.columns(2)
    for idx, query in enumerate(example_queries):
        with cols[idx % 2]:
            if st.button(f"{query}", key=f"example_{idx}", use_container_width=True):
                handle_user_input(query)

    st.divider()

    st.info("**提示**：您可以直接在下方输入框告诉我您的旅行需求，比如目的地、预算、天数等，我会为您制定专属方案！")

# 显示消息历史
message_container = st.container()
with message_container:
    for msg_idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            display_user_message(message["content"])
        else:
            display_ai_message(message, msg_idx)

# 输入框
user_input = st.chat_input(
    "告诉我您的旅行需求...",
    key="chat_input"
)

if user_input:
    handle_user_input(user_input)

# 页脚
with st.container():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("TripPilot v2.0 - 您的智能旅行伙伴")

    with col2:
        if st.session_state.messages:
            last_msg_time = datetime.now().strftime("%H:%M")
            st.caption(f"最后更新: {last_msg_time}")

    with col3:
        st.caption("💡 提示：可以在侧边栏管理多个对话")