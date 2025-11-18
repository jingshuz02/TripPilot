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

# --------------- 初始化全局状态 (保持原样，防止数据丢失) ---------------
# 初始化API客户端
if "api_client" not in st.session_state:
#try:
    from api_client import APIClient
    st.session_state.api_client = APIClient()
    # except ImportError:
    #     # 模拟一个假的 Client
    #     class MockClient:
    #         def check_health(self): return True
    #         def chat(self, **kwargs): 
    #             return {
    #                 "action": "suggestion", 
    #                 "content": "Mock响应：后端未连接，请检查 api_client.py",
    #                 "data": {}
    #             }
    #     st.session_state.api_client = MockClient()

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
    st.session_state.budget = 1000  # 恢复默认1000

# 初始化API连接状态
if "api_connected" not in st.session_state:
    st.session_state.api_connected = getattr(st.session_state.api_client, 'check_health', lambda: False)()

# 确保当前对话的消息列表存在
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
if "messages" not in current_conv:
    current_conv["messages"] = []

# --------------- 辅助函数：处理预订 (保持原样) ---------------
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

@st.dialog("航班详情")
def show_flight_details_dialog(flight):
    # 优先使用 flight 数据里的 amenities，如果没有则使用原来的模拟数据
    amenities = flight.get("amenities", [])
    if not amenities:
        amenities = [
            {"service": "机上餐饮", "is_chargeable": False},
            {"service": "Wi-Fi", "is_chargeable": True},
            {"service": "USB充电", "is_chargeable": False}
        ]
    display_flight_details_modal(flight, amenities)

# --------------- 页面配置 ---------------
st.set_page_config(
    page_title="TripPilot - Chat",
    page_icon="💬",
    layout="wide"
)

st.title("💬 Chat with TripPilot")

# --------------- 侧边栏 (功能已恢复) ---------------
with st.sidebar:
    # 1. 对话管理
    st.header("🗨️ 对话管理")
    if st.button("+ 新建对话", use_container_width=True):
        new_conv_id = f"conv_{len(st.session_state.conversations)}"
        st.session_state.conversations[new_conv_id] = {
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.active_conv_id = new_conv_id
        st.rerun()
    
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

    # 2. 旅行偏好设置 (已恢复预算输入框)
    st.header("🎯 旅行偏好")
    # 计算剩余预算
    total_spent = sum(o['price'] for o in st.session_state.orders)
    initial_budget = st.session_state.budget
    remaining_budget = initial_budget - total_spent
    
    st.metric("剩余预算", f"${remaining_budget}", delta=f"-${total_spent}" if total_spent > 0 else None)
    
    # [恢复] 这里是你原本用来调节总预算的输入框
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
        "budget": remaining_budget, 
        "total_budget": initial_budget,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "language": language
    }
    st.divider()

    # 3. 订单记录展示 (已恢复)
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
# --------------- 聊天内容展示逻辑 (根据新JSON重构) ---------------

# 获取当前对话的消息列表
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
messages = current_conv["messages"]

# 1. 渲染历史消息
for idx, msg in enumerate(messages):
    with st.chat_message(msg["role"]):
        # A. 渲染文本内容
        # 统一使用 content 字段 (无论是 suggestion 还是 search_xxx 的附带文本)
        content_text = msg.get("content")
        if content_text:
            st.markdown(content_text)
        
        # B. 渲染组件 (根据 action 字段)
        action_type = msg.get("action")
        data_payload = msg.get("data")
        
        # --- 渲染酒店 ---
        if action_type == "search_hotels" and isinstance(data_payload, list):
            st.markdown("---")
            st.subheader("🏨 推荐酒店")
            for i, hotel in enumerate(data_payload):
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

        # --- 渲染航班 ---
        elif action_type == "search_flights" and isinstance(data_payload, list):
            st.markdown("---")
            st.subheader("✈️ 推荐航班")
            for i, flight in enumerate(data_payload):
                unique_key = f"hist_{idx}_flight_{flight.get('id', i)}"
                # 调用组件
                action = display_flight_card(flight, key_prefix=unique_key)
                # 处理回调
                if action == "book":
                    handle_booking(
                        "flight", 
                        f"{flight.get('carrier_code')}{flight.get('flight_number')}", 
                        flight.get('total_price', 0)
                    )
                    st.rerun()
                elif action == "details":
                    show_flight_details_dialog(flight)

        # --- 渲染天气 ---
        elif action_type == "get_weather" and isinstance(data_payload, dict):
            st.markdown("---")
            # 天气通常不需要循环，因为一次只查一个目的地
            display_weather(data_payload, city_name=data_payload.get("city_name", "目的地"))


# 2. 处理用户输入
if prompt := st.chat_input("请输入您的旅行需求..."):
    
    # 记录用户消息
    messages.append({"role": "user", "content": prompt})
    st.rerun()

# 3. 触发后端响应
if messages and messages[-1]["role"] == "user":
    
    last_user_msg = messages[-1]["content"]
    
    with st.chat_message("assistant"):
        with st.spinner("正在规划您的旅程..."):
            
            if not st.session_state.api_connected:
                st.error("⚠️ 后端服务未连接，请先启动服务器。")
                st.stop()

            # --- 调用 API (只调用一次) ---
            try:
                # 发送给后端的参数
                backend_response = st.session_state.api_client.chat(
                    prompt=last_user_msg,
                    preferences=travel_preferences
                )
                
                # 预期后端返回格式:
                # { 
                #   "action": "search_flights" | "suggestion" | ..., 
                #   "content": "文本描述...", 
                #   "data": [...] or {...}
                # }
                
                if not backend_response:
                    st.error("后端无响应")
                    st.stop()

                # 将响应转换为消息格式
                new_msg = backend_response.copy()
                new_msg["role"] = "assistant"
                
                # 保存消息
                messages.append(new_msg)
                
                # 刷新以显示结果
                st.rerun()

            except Exception as e:
                st.error(f"调用失败: {str(e)}")
                st.stop()
