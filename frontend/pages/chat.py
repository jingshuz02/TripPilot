


import sys
import os
# 将项目根目录添加到 python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
import streamlit as st
from datetime import datetime, timedelta
from uuid import uuid4

from frontend.components.weather_widget import display_weather
from frontend.components.hotel_card import display_hotel_card
from frontend.components.flight_card import display_flight_card, display_flight_details_modal
# 引入自定义组件


# --------------- 初始化全局状态 ---------------
# 初始化API客户端
if "api_client" not in st.session_state:
    # 假设目录下有 api_client.py，如果没有请自行调整
    try:
        from api_client import APIClient
        st.session_state.api_client = APIClient()
    except ImportError:
        # 模拟一个假的 Client 以防报错
        class MockClient:
            def check_health(self): return True
            def chat(self, **kwargs): return {}
        st.session_state.api_client = MockClient()

# 初始化多对话存储
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "conv_0": {
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }
if "active_conv_id" not in st.session_state:
    st.session_state.active_conv_id = "conv_0"

# 初始化订单和行程数据
if "orders" not in st.session_state:
    st.session_state.orders = []
if "trips" not in st.session_state:
    st.session_state.trips = [{
        "name": "Default Trip",
        "id": str(uuid4())[:8],
        "created_at": datetime.now().strftime("%Y-%m-%d")
    }]
if "budget" not in st.session_state:
    st.session_state.budget = 1000

# 初始化API连接状态
if "api_connected" not in st.session_state:
    st.session_state.api_connected = getattr(st.session_state.api_client, 'check_health', lambda: False)()

# 确保当前对话的消息列表存在
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
if "messages" not in current_conv:
    current_conv["messages"] = []

# --------------- 辅助函数：处理预订 ---------------
def handle_booking(item_type, item_data, price):
    order_id = str(uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # 获取当前活跃的对话 ID
    current_conv_id = st.session_state.get("active_conv_id", "conv_0")
    
    new_order = {
        "id": order_id,
        "type": item_type,
        "item": item_data,
        "price": price,
        "time": timestamp,
        "status": "已确认",
        "conversation_id": current_conv_id 
    }
    
    # 确保全局订单列表存在
    if "orders" not in st.session_state:
        st.session_state.orders = []
        
    st.session_state.orders.append(new_order)
    st.toast(f"✅ 预订成功！(关联对话: {current_conv_id})", icon="🎉")

# --------------- 页面配置 ---------------
st.set_page_config(
    page_title="TripPilot - Chat",
    page_icon="💬",
    layout="wide"
)

# --------------- 页面标题 ---------------
st.title("💬 Chat with TripPilot")

# --------------- 侧边栏 ---------------
with st.sidebar:
    # 1. 对话管理
    st.header("🗨️ 对话管理")
    # 新建对话按钮
    if st.button("+ 新建对话", use_container_width=True):
        new_conv_id = f"conv_{len(st.session_state.conversations)}"
        st.session_state.conversations[new_conv_id] = {
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.active_conv_id = new_conv_id
        st.rerun()
    
    # 对话选择下拉框
    conv_options = {
        conv_id: f"对话 {i+1} ({data['created_at']})" 
        for i, (conv_id, data) in enumerate(st.session_state.conversations.items())
    }
    selected_conv_id = st.selectbox(
        "选择对话",
        options=list(conv_options.keys()),
        format_func=lambda x: conv_options[x],
        index=list(conv_options.keys()).index(st.session_state.active_conv_id)
    )
    if selected_conv_id != st.session_state.active_conv_id:
        st.session_state.active_conv_id = selected_conv_id
        st.rerun()
    st.divider()

    # 2. 旅行偏好设置
    st.header("🎯 旅行偏好")
    # 计算剩余预算
    total_spent = sum(o['price'] for o in st.session_state.orders)
    initial_budget = st.session_state.budget
    remaining_budget = initial_budget - total_spent
    
    st.metric("剩余预算", f"${remaining_budget}", delta=f"-${total_spent}" if total_spent > 0 else None)
    
    budget_input = st.number_input(
        "总预算 (USD)",
        min_value=0,
        value=initial_budget,
        step=100,
        key="travel_budget_input"
    )
    if budget_input != initial_budget:
        st.session_state.budget = budget_input
        st.rerun()
        
    start_date = st.date_input(
        "出发日期",
        value=datetime.now(),
        key="start_date"
    )
    end_date = st.date_input(
        "返回日期",
        value=datetime.now() + timedelta(days=3),
        key="end_date"
    )
    language = st.selectbox(
        "语言",
        ["中文", "English", "日本語"],
        key="language"
    )
    
    travel_preferences = {
        "budget": remaining_budget, # 传给 Agent 剩余预算
        "total_budget": initial_budget,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "language": language
    }
    st.divider()

    # 3. 订单记录展示
    st.header("📋 订单记录")
    if st.session_state.orders:
        for order in st.session_state.orders:
            icon = "🏨" if order['type'] == 'hotel' else "✈️"
            with st.expander(f"{icon} {order['item']} - ${order['price']}"):
                st.caption(f"订单号: {order['id']}")
                st.caption(f"时间: {order['time']}")
                st.write(f"状态: **{order['status']}**")
    else:
        st.info("暂无订单")
    st.divider()

    # 4. 后端连接状态
    st.header("⚙️ 连接状态")
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.api_connected:
            st.success("✅ 后端已连接")
        else:
            st.error("❌ 后端未连接")
    with col2:
        if st.button("🔄"):
            st.session_state.api_connected = getattr(st.session_state.api_client, 'check_health', lambda: False)()
            st.rerun()
            
    # 开发者工具：清空当前对话
    if st.button("🗑️ 清空当前对话"):
        st.session_state.conversations[st.session_state.active_conv_id]["messages"] = []
        st.rerun()


# --------------- 聊天内容展示逻辑 ---------------

@st.dialog("航班详情")
def show_flight_details_dialog(flight):
    # 模拟 amenity 数据，实际应从 flight 数据中获取
    mock_amenities = [
        {"service": "机上餐饮", "is_chargeable": False},
        {"service": "Wi-Fi", "is_chargeable": True},
        {"service": "USB充电", "is_chargeable": False}
    ]
    display_flight_details_modal(flight, mock_amenities)

# 获取当前对话的消息列表
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
messages = current_conv["messages"]

# 1. 渲染历史消息（包含组件）
#    注意：我们需要给每个组件一个唯一的key，避免冲突
for idx, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        # 显示文本内容
        if msg.get("content"):
            st.markdown(msg["content"])
        
        # 显示 Payload 组件内容 (如果存在)
        payload = msg.get("payload")
        if payload:
            p_type = payload.get("type")
            p_data = payload.get("data")
            
            # --- 渲染酒店列表 ---
            if p_type == "hotels" and isinstance(p_data, list):
                st.markdown("---")
                st.subheader("🏨 推荐酒店")
                for i, hotel in enumerate(p_data):
                    # 生成唯一 key
                    unique_key = f"hist_{idx}_hotel_{hotel.get('id', i)}"
                    
                    # 调用组件
                    action = display_hotel_card(hotel, key_prefix=unique_key)
                    
                    # 处理回调
                    if action == "book":
                        handle_booking(
                            "hotel", 
                            hotel.get('name', '未知酒店'), 
                            hotel.get('total_price', 0)
                        )
                        st.rerun()

            # --- 渲染航班列表 ---
            elif p_type == "flights" and isinstance(p_data, list):
                st.markdown("---")
                st.subheader("✈️ 推荐航班")
                for i, flight in enumerate(p_data):
                    unique_key = f"hist_{idx}_flight_{flight.get('id', i)}"
                    
                    action = display_flight_card(flight, key_prefix=unique_key)
                    
                    if action == "book":
                        handle_booking(
                            "flight", 
                            f"{flight.get('carrier_code')}{flight.get('flight_number')}", 
                            flight.get('total_price', 0)
                        )
                        st.rerun()
                    elif action == "details":
                        show_flight_details_dialog(flight)

            # --- 渲染天气组件 ---
            elif p_type == "weather" and isinstance(p_data, dict):
                st.markdown("---")
                # 天气可以直接展示，不需要交互 key
                display_weather(p_data, city_name=payload.get("city_name", "目的地"))

            # --- 渲染行程 (暂略) ---
            elif p_type == "schedule":
                st.info("📅 行程展示功能开发中...")
                with st.expander("查看原始数据"):
                    st.json(p_data)


# 2. 处理用户输入
if prompt := st.chat_input("请输入您的旅行需求...（例如：帮我订东京三晚的酒店）"):
    
    # 2.1 添加用户消息
    messages.append({"role": "user", "content": prompt})
    # 强制刷新以立即显示用户消息
    st.rerun()

# 注意：这里逻辑稍微调整，因为 st.chat_input 提交后会 rerun，
# 我们需要在 rerun 的这一次执行中，检测到最后一条消息是 user，然后触发 assistant 回复
if messages and messages[-1]["role"] == "user":
    
    last_user_msg = messages[-1]["content"]
    
    with st.chat_message("assistant"):
        with st.spinner("正在规划您的旅程..."):
            
            # --- A. 检查连接 ---
            if not st.session_state.api_connected:
                st.error("⚠️ 后端服务未连接")
                messages.append({"role": "assistant", "content": "⚠️ 后端服务未连接，请先启动服务器。"})
                st.stop()

            # --- B. 调用 API ---
            try:
                # 实际调用
                backend_response = st.session_state.api_client.chat(
                    prompt=last_user_msg,
                    preferences=travel_preferences
                )
            except Exception as e:
                st.error(f"调用失败: {str(e)}")
                st.stop()

            # --- C. 解析响应 ---
            if not backend_response:
                st.error("后端无响应")
                st.stop()

            action = backend_response.get("action")
            params = backend_response.get("params", {})
            reply_text = backend_response.get("content", "")
            
            # 准备构建新的消息对象
            new_msg = {
                "role": "assistant", 
                "content": reply_text,
                "payload": None 
            }

            # ==========================================
            #  ACTION 1: 搜索酒店
            # ==========================================
            if action == "search_hotels":
                search_result = st.session_state.api_client.search_hotels(
                    city=params.get("city", ""),
                    check_in=params.get("check_in", travel_preferences.get("start_date")),
                    check_out=params.get("check_out", travel_preferences.get("end_date")),
                    budget=travel_preferences.get("budget")
                )
                hotel_ids = search_result.get("hotel_ids", []) if search_result else []
                
                hotels_data = []
                if hotel_ids:
                    for h_id in hotel_ids[:5]: # 限制显示前5个
                        detail = st.session_state.api_client.get_hotel_details(h_id)
                        if detail: hotels_data.append(detail)
                
                if hotels_data:
                    new_msg["content"] += "\n\n已为您找到以下推荐酒店："
                    new_msg["payload"] = {"type": "hotels", "data": hotels_data}
                else:
                    new_msg["content"] += "\n\n(抱歉，未找到符合条件的酒店)"

            # ==========================================
            #  ACTION 2: 搜索航班
            # ==========================================
            elif action == "search_flights":
                flight_ids = st.session_state.api_client.search_flights(
                    origin=params.get("origin", ""),
                    destination=params.get("destination", ""),
                    date=params.get("date", travel_preferences.get("start_date")),
                )
                
                flights_data = []
                if flight_ids:
                    for f_id in flight_ids[:5]:
                        detail = st.session_state.api_client.get_flight_details(f_id)
                        if detail: flights_data.append(detail)

                if flights_data:
                    new_msg["content"] += "\n\n已为您找到以下推荐航班："
                    new_msg["payload"] = {"type": "flights", "data": flights_data}
                else:
                    new_msg["content"] += "\n\n(抱歉，未找到符合条件的航班)"

            # ==========================================
            #  ACTION 3: 天气查询
            # ==========================================
            elif action == "get_weather":
                city = params.get("city", "Unknown")
                weather_data = st.session_state.api_client.get_weather(
                    city=city,
                    start_date=params.get("start_date", ""),
                    end_date=params.get("end_date", "")
                )
                
                if weather_data:
                    new_msg["content"] += f"\n\n这是 {city} 当地的天气情况："
                    new_msg["payload"] = {
                        "type": "weather", 
                        "data": weather_data,
                        "city_name": city
                    }

            # ==========================================
            #  ACTION 4: 行程 (Placeholder)
            # ==========================================
            elif action == "search_schedule":
                 schedule_data = st.session_state.api_client.search_schedule(
                    destination=params.get("destination", ""),
                    # ... params
                )
                 if schedule_data:
                     new_msg["content"] += "\n\n行程安排已生成。"
                     new_msg["payload"] = {"type": "schedule", "data": schedule_data}

            # --- D. 保存并刷新 ---
            messages.append(new_msg)
            st.rerun()
