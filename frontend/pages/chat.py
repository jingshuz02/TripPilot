"""
TripPilot 聊天界面 - 修复版 + 组件集成版
修复了：
1. Streamlit重复key错误 - 在key中加入消息索引
2. 前端超时时间增加到90秒
3. 集成了自定义组件（hotel_card, weather_widget, flight_card）
"""

import streamlit as st
import requests
from datetime import datetime
import json

# ==================== 导入自定义组件 ====================
# 酒店组件
try:
    from components.hotel_card import display_hotel_card_v2, display_hotel_list_v2
except ImportError:
    display_hotel_list_v2 = None
    display_hotel_card_v2 = None

# 天气组件
try:
    from components.weather_widget import display_weather_enhanced
except ImportError:
    display_weather_enhanced = None

# 机票组件
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

# ==================== 初始化会话状态（修复版） ====================
def init_session_state():
    """初始化所有必要的会话状态 - 确保所有值都有效"""

    # 消息历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 当前行程信息 - 确保所有值都初始化正确
    if "current_trip" not in st.session_state:
        st.session_state.current_trip = {
            "destination": "",
            "days": 3,
            "budget": 5000,
            "start_date": datetime.now().date(),
            "end_date": None
        }
    else:
        trip = st.session_state.current_trip
        if trip.get("days", 0) < 1:
            trip["days"] = 3
        if trip.get("budget", 0) < 500:
            trip["budget"] = 5000
        if trip.get("start_date") is None:
            trip["start_date"] = datetime.now().date()

    # 订单列表
    if "orders" not in st.session_state:
        st.session_state.orders = []

    # 对话历史管理
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d%H%M%S')}"

# 立即初始化
init_session_state()

# ==================== 样式定义 ====================
st.markdown("""
<style>
    /* 整体背景 */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* 用户消息样式 */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 18px;
        padding: 12px 20px;
        margin: 10px 0;
        margin-left: 20%;
        box-shadow: 0 3px 15px rgba(102, 126, 234, 0.3);
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
    .ai-message h1 { color: #1a73e8; font-size: 1.5rem; margin: 1rem 0; }
    .ai-message h2 { color: #1976d2; font-size: 1.3rem; margin: 0.8rem 0; }
    .ai-message h3 { color: #1e88e5; font-size: 1.1rem; margin: 0.6rem 0; }
    .ai-message strong { color: #1565c0; font-weight: 600; }
    .ai-message ul { margin: 0.5rem 0; padding-left: 1.5rem; }
    .ai-message li { margin: 0.3rem 0; line-height: 1.6; }
    
    /* 快速建议按钮 */
    .suggestion-btn {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 8px 16px;
        margin: 4px;
        cursor: pointer;
        transition: all 0.3s;
        display: inline-block;
    }
    
    .suggestion-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 信息卡片 */
    .info-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    /* 加载动画 */
    .loading-dots {
        display: inline-block;
        animation: loading 1.4s infinite;
    }
    
    @keyframes loading {
        0% { content: '.'; }
        33% { content: '..'; }
        66% { content: '...'; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== API 交互函数 ====================
def call_backend_api(message: str) -> dict:
    """调用后端API获取回复"""
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

        # ✅ 修复：增加前端超时时间到90秒
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
                "content": f"😕 服务器返回了错误状态：{response.status_code}\n请稍后重试或联系支持。",
                "data": None,
                "suggestions": ["重新发送", "查看帮助"]
            }

    except requests.exceptions.Timeout:
        return {
            "action": "error",
            "content": "⏱️ 请求超时了，可能是网络较慢或服务器繁忙。\n请稍后重试。",
            "data": None,
            "suggestions": ["重新发送", "检查网络"]
        }
    except requests.exceptions.ConnectionError:
        return {
            "action": "error",
            "content": "❌ 无法连接到后端服务\n\n请确保后端已启动：\n```bash\npython app.py\n```",
            "data": None,
            "suggestions": ["启动后端", "查看文档"]
        }
    except Exception as e:
        return {
            "action": "error",
            "content": f"😵 发生了意外错误：\n{str(e)}\n\n请尝试重新发送消息。",
            "data": None,
            "suggestions": ["重新发送", "报告问题"]
        }

# ==================== 消息显示函数 ====================
def display_user_message(content: str):
    """显示用户消息"""
    st.markdown(f'<div class="user-message">👤 {content}</div>', unsafe_allow_html=True)


def display_ai_message(message: dict, msg_idx: int = 0):
    """显示AI消息 - 增强版"""
    content = message.get("content", "")
    action = message.get("action", "")
    data = message.get("data", None)

    # 显示主要内容
    if content:
        if action == "error":
            st.error(content)
        else:
            st.markdown(f'<div class="ai-message">🤖 {content}</div>', unsafe_allow_html=True)

    # 根据action类型显示额外数据
    if data:
        if action == "search_hotels":
            display_hotel_results(data, msg_idx)
        elif action == "search_flights":
            display_flight_results(data, msg_idx)
        elif action == "weather" or action == "get_weather":
            display_weather_info(data, msg_idx)

    # 显示建议按钮
    suggestions = message.get("suggestions", [])
    if suggestions:
        display_suggestions(suggestions, msg_idx)


# ==================== 酒店展示 ====================
def display_hotel_results(hotels: list, msg_idx: int = 0):
    """显示酒店搜索结果 - 使用自定义组件"""
    if not hotels:
        return

    # ✅ 优先使用自定义组件
    if display_hotel_list_v2 is not None:
        display_hotel_list_v2(hotels, message_id=msg_idx)
    else:
        # 备用展示
        _display_hotel_fallback(hotels, msg_idx)


def _display_hotel_fallback(hotels: list, msg_idx: int = 0):
    """酒店备用展示"""
    with st.expander("🏨 查看酒店详情", expanded=True):
        for idx, hotel in enumerate(hotels[:5], 1):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            with col1:
                st.write(f"**{idx}. {hotel.get('name', '未知酒店')}**")
                st.caption(f"📍 {hotel.get('location', '未知位置')}")
            with col2:
                rating = hotel.get('rating', 0)
                st.write(f"⭐ {rating:.1f}")
            with col3:
                price = hotel.get('price', 0)
                st.write(f"💰 ¥{price}")
            with col4:
                if st.button("预订", key=f"hotel_{msg_idx}_{idx}_{hotel.get('id', idx)}"):
                    add_to_orders("hotel", hotel)
            if idx < len(hotels[:5]):
                st.divider()


# ==================== 机票展示 ====================
def display_flight_results(flights: list, msg_idx: int = 0):
    """显示航班搜索结果 - 使用自定义组件"""
    if not flights:
        return

    # ✅ 优先使用自定义组件
    if display_flight_list_v2 is not None:
        display_flight_list_v2(flights, message_id=msg_idx)
    else:
        # 备用展示
        _display_flight_fallback(flights, msg_idx)


def _display_flight_fallback(flights: list, msg_idx: int = 0):
    """机票备用展示"""
    with st.expander("✈️ 查看航班详情", expanded=True):
        for idx, flight in enumerate(flights[:5], 1):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                flight_no = f"{flight.get('carrier_code', '')}{flight.get('flight_number', '')}"
                st.write(f"**{idx}. {flight_no}**")
                times = f"🛫 {flight.get('departure_time', 'N/A')} → 🛬 {flight.get('arrival_time', 'N/A')}"
                st.caption(times)
            with col2:
                price = flight.get('total_price', flight.get('price', 0))
                st.write(f"💰 ¥{price}")
            with col3:
                if st.button("预订", key=f"flight_{msg_idx}_{idx}_{flight.get('id', idx)}"):
                    add_to_orders("flight", flight)
            if idx < len(flights[:5]):
                st.divider()


# ==================== 天气展示 ====================
def display_weather_info(weather_data: dict, msg_idx: int = 0):
    """显示天气信息 - 使用自定义组件"""
    if not weather_data:
        return

    city_name = weather_data.get('city', weather_data.get('location', '目的地'))

    # 处理数据格式
    if 'current' in weather_data:
        current = weather_data['current']
        formatted_weather = {
            'temperature': current.get('temperature', 20),
            'feels_like': current.get('feels_like', current.get('temperature', 20)),
            'weather': current.get('weather', current.get('description', '晴朗')),
            'humidity': current.get('humidity', 60),
            'wind_speed': current.get('wind_speed', '3.0 m/s')
        }
    else:
        formatted_weather = {
            'temperature': weather_data.get('temperature', 20),
            'feels_like': weather_data.get('feels_like', weather_data.get('temperature', 20)),
            'weather': weather_data.get('weather', weather_data.get('description', '晴朗')),
            'humidity': weather_data.get('humidity', 60),
            'wind_speed': weather_data.get('wind_speed', '3.0 m/s')
        }

    # ✅ 优先使用自定义组件
    if display_weather_enhanced is not None:
        display_weather_enhanced(formatted_weather, city_name)
    else:
        # 备用展示
        _display_weather_fallback(formatted_weather)


def _display_weather_fallback(weather: dict):
    """天气备用展示"""
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🌡️ 温度", f"{weather['temperature']}°C")
        with col2:
            st.metric("💧 湿度", f"{weather['humidity']}%")
        with col3:
            st.metric("💨 风速", f"{weather['wind_speed']}")
        with col4:
            st.metric("🌤️ 天气", weather['weather'])


# ==================== 建议按钮 ====================
def display_suggestions(suggestions: list, msg_idx: int = 0):
    """显示建议按钮"""
    if not suggestions:
        return

    st.markdown("**💡 您可能还想了解：**")
    cols = st.columns(min(len(suggestions[:3]), 3))
    for idx, (col, suggestion) in enumerate(zip(cols, suggestions[:3])):
        with col:
            # ✅ key中加入msg_idx确保唯一性
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
    st.success(f"✅ 已添加到订单！共 {len(st.session_state.orders)} 个订单")
    st.balloons()


# ==================== 主函数 ====================
def handle_user_input(message: str):
    """处理用户输入"""
    if not message.strip():
        return

    st.session_state.messages.append({
        "role": "user",
        "content": message
    })

    with st.spinner("🤔 AI正在思考，请稍候..."):
        response = call_backend_api(message)

    st.session_state.messages.append({
        "role": "assistant",
        **response
    })

    st.rerun()


# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("⚙️ 旅行设置")

    st.subheader("🗺️ 行程信息")

    destination = st.text_input(
        "目的地",
        value=st.session_state.current_trip.get("destination", ""),
        placeholder="例如：成都、杭州、东京",
        help="输入您想去的城市或地区"
    )
    st.session_state.current_trip["destination"] = destination

    col1, col2 = st.columns(2)
    with col1:
        current_days = st.session_state.current_trip.get("days", 3)
        if not isinstance(current_days, int) or current_days < 1:
            current_days = 3
            st.session_state.current_trip["days"] = 3

        days = st.number_input(
            "天数",
            min_value=1,
            max_value=30,
            value=current_days,
            step=1,
            help="旅行天数（1-30天）"
        )
        st.session_state.current_trip["days"] = days

    with col2:
        current_budget = st.session_state.current_trip.get("budget", 5000)
        if not isinstance(current_budget, (int, float)) or current_budget < 500:
            current_budget = 5000
            st.session_state.current_trip["budget"] = 5000

        budget = st.number_input(
            "预算 (¥)",
            min_value=500,
            max_value=100000,
            value=int(current_budget),
            step=500,
            help="总预算金额"
        )
        st.session_state.current_trip["budget"] = budget

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "开始日期",
            value=st.session_state.current_trip.get("start_date", datetime.now().date()),
            min_value=datetime.now().date(),
            help="旅行开始日期"
        )
        st.session_state.current_trip["start_date"] = start_date

    with col2:
        from datetime import timedelta
        default_end = start_date + timedelta(days=days-1)

        end_date = st.date_input(
            "结束日期",
            value=default_end,
            min_value=start_date,
            help="旅行结束日期"
        )
        st.session_state.current_trip["end_date"] = end_date

    st.divider()

    st.subheader("🚀 快速操作")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.success("对话已清空")
            st.rerun()

    with col2:
        if st.button("📋 查看订单", use_container_width=True):
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

    st.caption(f"""
    **📊 当前状态**
    - 💬 消息数: {len(st.session_state.messages)}
    - 📍 目的地: {destination or '未设置'}
    - 💰 预算: ¥{budget:,}
    - 📅 天数: {days}天
    - 🗓️ 日期: {start_date.strftime('%m/%d')} - {end_date.strftime('%m/%d')}
    """)

    try:
        response = requests.get("http://localhost:5000/health", timeout=1)
        if response.status_code == 200:
            st.success("🟢 后端已连接")
        else:
            st.error("🔴 后端异常")
    except:
        st.error("🔴 后端未启动")
        st.caption("运行: `python app.py`")


# ==================== 主界面 ====================
st.title("💬 TripPilot 智能旅行助手")
st.caption("✨ 基于 DeepSeek AI | 让旅行规划变得简单有趣")

if not st.session_state.messages:
    st.markdown("""
    <div class="info-card">
    <h3>👋 您好！我是您的专属AI旅行助手</h3>
    <p>我可以为您提供个性化的旅行服务，包括行程规划、酒店推荐、航班查询等。</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **🗺️ 行程规划**
        - 详细的每日安排
        - 景点路线优化
        - 时间分配建议
        """)

    with col2:
        st.markdown("""
        **🏨 住宿推荐**
        - 各档次酒店选择
        - 位置优势分析
        - 性价比排序
        """)

    with col3:
        st.markdown("""
        **✈️ 交通安排**
        - 航班时刻查询
        - 最优路线推荐
        - 交通工具建议
        """)

    st.divider()

    st.subheader("🎯 快速开始 - 点击试试")

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
            if st.button(f"💡 {query}", key=f"example_{idx}", use_container_width=True):
                handle_user_input(query)

    st.divider()

    st.info("💡 **提示**：您可以直接在下方输入框告诉我您的旅行需求，比如目的地、预算、天数等，我会为您制定专属方案！")

message_container = st.container()
with message_container:
    for msg_idx, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            display_user_message(message["content"])
        else:
            display_ai_message(message, msg_idx)

user_input = st.chat_input(
    "💬 告诉我您的旅行需求...",
    key="chat_input"
)

if user_input:
    handle_user_input(user_input)

with st.container():
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🤝 TripPilot v2.0 - 您的智能旅行伙伴")

    with col2:
        if st.session_state.messages:
            last_msg_time = datetime.now().strftime("%H:%M")
            st.caption(f"⏰ 最后更新: {last_msg_time}")

    with col3:
        st.caption("💭 有问题？试试问我如何规划行程")