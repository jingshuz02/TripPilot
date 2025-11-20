"""
改进版聊天页面 - 修复导入路径和多对话功能
智能展示各类数据，支持详情查看和筛选
"""

import streamlit as st
from datetime import datetime
import sys
import os
import requests

# 修复导入路径问题
# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 现在使用相对导入
try:
    # 尝试从components导入
    from components.hotel_card import display_hotel_card
    from components.flight_card import display_flight_card
except ImportError:
    # 如果components不存在，使用内置函数
    st.warning("组件文件未找到，使用内置显示功能")

    def display_hotel_card(hotel, key_prefix="hotel"):
        """内置的酒店卡片显示函数"""
        with st.container(border=True):
            st.subheader(hotel.get('name', 'Unknown Hotel'))
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"📍 {hotel.get('location', 'N/A')}")
                st.write(f"⭐ {hotel.get('rating', 'N/A')}/5")
            with col2:
                st.write(f"💰 ¥{hotel.get('price', 0)}/晚")
            with col3:
                if st.button("选择", key=f"{key_prefix}_select"):
                    return "book"
        return None

    def display_flight_card(flight_data, key_prefix="flight"):
        """内置的航班卡片显示函数"""
        with st.container(border=True):
            flight_num = f"{flight_data.get('carrier_code', 'XX')}{flight_data.get('flight_number', '000')}"
            st.subheader(flight_num)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"🛫 {flight_data.get('departure', 'N/A')}")
                st.write(f"🛬 {flight_data.get('arrival', 'N/A')}")
            with col2:
                st.write(f"⏱️ {flight_data.get('duration', 'N/A')}")
            with col3:
                st.write(f"💰 ¥{flight_data.get('total_price', 0)}")
                if st.button("选择", key=f"{key_prefix}_select"):
                    return "book"
        return None

try:
    from weather_widget import display_weather_compact, get_mock_weather_data
except ImportError:
    def display_weather_compact(weather_data, city_name="城市", forecast_days=3):
        """简单的天气显示"""
        st.info(f"{city_name}: {weather_data.get('temperature', 20)}°C")

    def get_mock_weather_data(city_name="城市"):
        """模拟天气数据"""
        return {'temperature': 20, 'description': '晴', 'humidity': 60}

# ==================== 辅助函数定义 ====================

def calculate_nights(start_date, end_date):
    """计算晚数"""
    try:
        if isinstance(start_date, str):
            start = datetime.strptime(start_date, "%Y-%m-%d")
        else:
            start = start_date

        if isinstance(end_date, str):
            end = datetime.strptime(end_date, "%Y-%m-%d")
        else:
            end = end_date

        return max((end - start).days, 1)
    except:
        return 1

def call_backend_api(prompt, preferences):
    """直接调用后端API"""
    try:
        response = requests.post(
            "http://localhost:5000/api/chat",
            json={
                "prompt": prompt,
                "preferences": preferences
            },
            timeout=30
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"API调用失败: {e}")
    return None

def show_hotel_details(hotel):
    """显示酒店详情"""
    st.write(f"**地址**: {hotel.get('address', 'N/A')}")
    st.write(f"**电话**: {hotel.get('tel', 'N/A')}")
    st.write(f"**评分**: {hotel.get('rating', 'N/A')}/5")

    st.markdown("**设施服务**")
    amenities = hotel.get('amenities', [])
    if amenities:
        cols = st.columns(3)
        for idx, amenity in enumerate(amenities):
            with cols[idx % 3]:
                st.write(f"✓ {amenity}")

    st.markdown("**价格信息**")
    st.write(f"每晚: ¥{hotel.get('price', 0)}")
    nights = calculate_nights(
        st.session_state.get('start_date', '2025-01-01'),
        st.session_state.get('end_date', '2025-01-02')
    )
    st.write(f"总价 ({nights}晚): ¥{hotel.get('price', 0) * nights}")

def add_to_selected(item, item_type):
    """添加到已选择列表"""
    selected_item = {
        "name": item.get('name', item.get('flight_number', 'Unknown')),
        "type": item_type,
        "price": item.get('price', item.get('total_price', 0)),
        "data": item
    }

    if selected_item not in st.session_state.selected_items:
        st.session_state.selected_items.append(selected_item)

def display_weather_info(weather_data):
    """显示天气信息"""
    if isinstance(weather_data, dict):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("温度", f"{weather_data.get('temperature', 'N/A')}°C")
        with col2:
            st.metric("天气", weather_data.get('description', weather_data.get('weather', 'N/A')))
        with col3:
            st.metric("湿度", f"{weather_data.get('humidity', 'N/A')}%")

def display_attractions_list(attractions):
    """显示景点列表"""
    st.info(f"找到 {len(attractions)} 个景点")

    for idx, attr in enumerate(attractions[:10]):
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.markdown(f"**{attr.get('name', 'Unknown')}**")
                st.write(f"📍 {attr.get('address', 'N/A')}")
                st.write(f"⭐ {attr.get('rating', 'N/A')}")
                st.write(f"🎫 {attr.get('price', '免费')}")

            with col2:
                if st.button("详情", key=f"attr_{idx}"):
                    st.info(attr.get('description', '暂无描述'))

def display_hotels_list(hotels):
    """显示酒店列表"""
    st.info(f"找到 {len(hotels)} 家酒店")

    with st.expander("🔍 筛选条件"):
        col1, col2 = st.columns(2)
        with col1:
            max_price = st.number_input("最高价格", value=9999, key="hotel_filter_price")
        with col2:
            min_rating = st.number_input("最低评分", value=0.0, key="hotel_filter_rating")

    for idx, hotel in enumerate(hotels[:10]):
        if hotel.get('price', 0) > max_price:
            continue
        if hotel.get('rating', 0) < min_rating:
            continue

        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"**{hotel.get('name', 'Unknown')}**")
                st.write(f"📍 {hotel.get('location', hotel.get('address', 'N/A'))}")
                st.write(f"⭐ {hotel.get('rating', 'N/A')}/5")

                amenities = hotel.get('amenities', [])
                if amenities:
                    amenities_text = " | ".join(amenities[:5])
                    st.caption(f"设施: {amenities_text}")

            with col2:
                st.metric("价格", f"¥{hotel.get('price', 0)}/晚")

            with col3:
                if st.button("查看详情", key=f"hotel_detail_{idx}"):
                    with st.expander(f"🏨 {hotel['name']} 详情", expanded=True):
                        show_hotel_details(hotel)

                if st.button("选择", key=f"hotel_select_{idx}", type="primary"):
                    add_to_selected(hotel, "hotel")
                    st.success("已添加到选择列表")
                    st.rerun()

def display_flights_list(flights):
    """显示航班列表"""
    st.info(f"找到 {len(flights)} 个航班")

    for idx, flight in enumerate(flights[:10]):
        with st.container(border=True):
            carrier_code = flight.get('carrier_code', flight.get('airline', 'XX'))
            flight_number = flight.get('flight_number', flight.get('flight_no', '000'))
            departure_time = flight.get('departure', flight.get('departure_time', 'N/A'))
            arrival_time = flight.get('arrival', flight.get('arrival_time', 'N/A'))

            col1, col2, col3 = st.columns([2, 1, 1])

            with col1:
                st.markdown(f"**{carrier_code}{flight_number}**")
                st.write(f"🛫 {departure_time} → 🛬 {arrival_time}")
                st.write(f"⏱️ {flight.get('duration', 'N/A')}")

            with col2:
                st.write(f"舱位: {flight.get('cabin_class', 'ECONOMY')}")
                st.write(f"机型: {flight.get('aircraft_code', 'N/A')}")

            with col3:
                st.metric("价格", f"¥{flight.get('total_price', flight.get('price', 0))}")

                if st.button("选择", key=f"flight_select_{idx}", type="primary"):
                    add_to_selected(flight, "flight")
                    st.success("已添加到选择列表")
                    st.rerun()

def display_itinerary(itinerary_data):
    """显示行程规划"""
    if isinstance(itinerary_data, dict):
        st.markdown("### 📅 行程规划")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("目的地", itinerary_data.get("destination", "N/A"))
        with col2:
            st.metric("天数", f"{itinerary_data.get('days', 0)}天")
        with col3:
            st.metric("预算", f"¥{itinerary_data.get('total_budget', 0)}")

        daily_plans = itinerary_data.get("daily_plans", [])
        for plan in daily_plans:
            with st.expander(f"第 {plan.get('day', 1)} 天"):
                st.write("**上午:**")
                for activity in plan.get("morning", []):
                    st.write(f"• {activity}")

                st.write("**下午:**")
                for activity in plan.get("afternoon", []):
                    st.write(f"• {activity}")

                st.write("**晚上:**")
                for activity in plan.get("evening", []):
                    st.write(f"• {activity}")

def display_message_content(message):
    """显示消息内容"""
    content = message.get("content", "")
    action = message.get("action", "")
    data = message.get("data", [])

    if content:
        st.markdown(content)

    if action == "search_hotels" and data:
        display_hotels_list(data)
    elif action == "search_flights" and data:
        display_flights_list(data)
    elif action == "get_weather" and data:
        display_weather_info(data)
    elif action == "search_attractions" and data:
        display_attractions_list(data)
    elif action == "full_planning" and data:
        display_itinerary(data)

    suggestions = message.get("suggestions", [])
    if suggestions:
        st.markdown("#### 💡 您可能还想了解")
        for sug in suggestions[:3]:
            if st.button(sug, key=f"sug_{hash(sug)}_{datetime.now().timestamp()}"):
                current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
                current_conv["messages"].append({"role": "user", "content": sug})
                st.rerun()

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="TripPilot Chat",
    page_icon="💬",
    layout="wide"
)

# ==================== 初始化session state ====================
if "conversations" not in st.session_state:
    st.session_state.conversations = {}
    default_id = "chat_1"
    st.session_state.conversations[default_id] = {
        "name": "对话 1",
        "messages": [],
        "created_at": datetime.now().isoformat()
    }
    st.session_state.current_conversation_id = default_id
    st.session_state.conversation_counter = 1

if "api_client" not in st.session_state:
    try:
        from api_client import APIClient
        st.session_state.api_client = APIClient()
    except ImportError:
        st.error("API客户端未找到，请确保api_client.py存在")

if "current_hotels" not in st.session_state:
    st.session_state.current_hotels = []
if "current_flights" not in st.session_state:
    st.session_state.current_flights = []
if "selected_items" not in st.session_state:
    st.session_state.selected_items = []
if "trip_context" not in st.session_state:
    st.session_state.trip_context = {}

# 自定义CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    border-radius: 10px;
    color: white;
    margin-bottom: 20px;
}
.chat-message {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
}
.user-message {
    background-color: #e3f2fd;
    margin-left: 20%;
}
.assistant-message {
    background-color: #f5f5f5;
    margin-right: 20%;
}
</style>
""", unsafe_allow_html=True)

# ==================== 侧边栏 ====================
with st.sidebar:
    st.markdown("### 💬 对话管理")

    # 新建对话
    if st.button("➕ 新建对话", use_container_width=True):
        st.session_state.conversation_counter += 1
        new_id = f"chat_{st.session_state.conversation_counter}"
        st.session_state.conversations[new_id] = {
            "name": f"对话 {st.session_state.conversation_counter}",
            "messages": [],
            "created_at": datetime.now().isoformat()
        }
        st.session_state.current_conversation_id = new_id
        st.rerun()

    # 对话列表
    st.markdown("**对话列表**")
    current_id = st.session_state.current_conversation_id

    for conv_id, conv_data in st.session_state.conversations.items():
        col1, col2, col3 = st.columns([3, 1, 1])

        with col1:
            prefix = "📌 " if conv_id == current_id else "  "
            if st.button(f"{prefix}{conv_data['name']}",
                        key=f"switch_{conv_id}",
                        use_container_width=True):
                st.session_state.current_conversation_id = conv_id
                st.rerun()

        with col2:
            if st.button("✏️", key=f"edit_{conv_id}"):
                st.session_state.edit_mode = conv_id
                st.rerun()

        with col3:
            if st.button("🗑️", key=f"delete_{conv_id}"):
                if len(st.session_state.conversations) > 1:
                    del st.session_state.conversations[conv_id]
                    if st.session_state.current_conversation_id == conv_id:
                        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
                    st.rerun()
                else:
                    st.warning("至少保留一个对话")

    # 编辑对话名称
    if hasattr(st.session_state, 'edit_mode'):
        st.markdown("---")
        st.markdown("**重命名对话**")
        edit_id = st.session_state.edit_mode
        new_name = st.text_input(
            "新名称",
            value=st.session_state.conversations[edit_id]['name'],
            key="rename_input"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ 确定", key="confirm_rename"):
                st.session_state.conversations[edit_id]['name'] = new_name
                del st.session_state.edit_mode
                st.rerun()
        with col2:
            if st.button("✕ 取消", key="cancel_rename"):
                del st.session_state.edit_mode
                st.rerun()

    st.divider()
    st.markdown("### 🎯 旅行偏好设置")

    # 预算设置
    col1, col2 = st.columns(2)
    with col1:
        budget = st.number_input(
            "💰 总预算(¥)",
            min_value=500,
            max_value=50000,
            value=st.session_state.get('budget', 5000),
            step=500
        )
    with col2:
        travelers = st.number_input(
            "👥 旅行人数",
            min_value=1,
            max_value=10,
            value=1
        )

    # 日期选择
    st.markdown("📅 **旅行日期**")
    col3, col4 = st.columns(2)
    with col3:
        start_date = st.date_input("开始日期", value=datetime.now().date())
    with col4:
        end_date = st.date_input("结束日期", value=datetime.now().date())

    # 酒店偏好
    st.markdown("🏨 **酒店偏好**")
    hotel_requirements = st.multiselect(
        "设施要求",
        ["WiFi", "停车场", "游泳池", "健身房", "早餐", "商务中心"],
        default=["WiFi"]
    )

    price_range = st.slider(
        "价格范围(¥/晚)",
        min_value=100,
        max_value=3000,
        value=(200, 1000),
        step=100
    )

    # 保存偏好
    preferences = {
        "budget": budget,
        "total_budget": budget,
        "travelers": travelers,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "hotel_requirements": hotel_requirements,
        "price_range": price_range,
        "language": "中文"
    }

    st.divider()

    # 天气显示
    st.markdown("### 🌤️ 目的地天气")
    destination_city = st.session_state.trip_context.get("destination", "北京")
    weather_data = get_mock_weather_data(destination_city)
    display_weather_compact(weather_data, destination_city, forecast_days=3)

    st.divider()

    # 已选择项目
    if st.session_state.selected_items:
        st.markdown("### 🛒 已选择")
        total_cost = 0
        for item in st.session_state.selected_items:
            st.write(f"• {item['name']}: ¥{item['price']}")
            total_cost += item['price']
        st.metric("总计", f"¥{total_cost}", f"剩余: ¥{budget - total_cost}")

# ==================== 辅助函数 - 添加快速建议 ====================
def add_quick_suggestion(suggestion):
    """添加快速建议作为用户消息"""
    conv_id = st.session_state.current_conversation_id
    st.session_state.conversations[conv_id]["messages"].append({
        "role": "user",
        "content": suggestion
    })
    st.session_state.process_suggestion = True

# ==================== 主聊天界面 ====================
st.markdown("<div class='main-header'><h1>🤖 TripPilot 智能旅行助手</h1><p>我是您的专属旅行顾问！</p></div>", unsafe_allow_html=True)

# 快捷建议
st.markdown("### 💡 快速开始")
suggestions = [
    "🏨 上海市中心的豪华酒店",
    "✈️ 明天北京到上海的航班",
    "📍 规划3天杭州旅游行程",
    "🎫 迪士尼门票价格"
]

cols = st.columns(len(suggestions))
for idx, (col, suggestion) in enumerate(zip(cols, suggestions)):
    with col:
        if st.button(suggestion, key=f"sug_{idx}", use_container_width=True):
            add_quick_suggestion(suggestion)
            st.rerun()

st.divider()

# ==================== 聊天历史 ====================
current_messages = st.session_state.conversations[st.session_state.current_conversation_id]["messages"]

for message in current_messages:
    with st.chat_message(message["role"]):
        if message["role"] == "user":
            st.write(message["content"])
        else:
            display_message_content(message)

# ==================== 输入框 ====================
# 处理快速建议
if st.session_state.get("process_suggestion", False):
    current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
    last_message = current_conv["messages"][-1]["content"]

    with st.chat_message("assistant"):
        with st.spinner("🤔 正在为您分析..."):
            try:
                if hasattr(st.session_state, 'api_client'):
                    response = st.session_state.api_client.chat(last_message, preferences)
                else:
                    response = call_backend_api(last_message, preferences)

                if response:
                    current_conv["messages"].append({
                        "role": "assistant",
                        "content": response.get("content", ""),
                        "action": response.get("action"),
                        "data": response.get("data"),
                        "suggestions": response.get("suggestions", [])
                    })
                    display_message_content(response)
                else:
                    st.error("无法获取响应，请检查后端服务是否运行")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")

    st.session_state.process_suggestion = False
    st.rerun()

# 处理聊天输入
if prompt := st.chat_input("💬 告诉我您的需求..."):
    current_conv = st.session_state.conversations[st.session_state.current_conversation_id]
    current_conv["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("🤔 正在为您分析..."):
            try:
                if hasattr(st.session_state, 'api_client'):
                    response = st.session_state.api_client.chat(prompt, preferences)
                else:
                    response = call_backend_api(prompt, preferences)

                if response:
                    current_conv["messages"].append({
                        "role": "assistant",
                        "content": response.get("content", ""),
                        "action": response.get("action"),
                        "data": response.get("data"),
                        "suggestions": response.get("suggestions", [])
                    })
                    display_message_content(response)
                else:
                    st.error("无法获取响应，请检查后端服务是否运行")
            except Exception as e:
                st.error(f"发生错误: {str(e)}")