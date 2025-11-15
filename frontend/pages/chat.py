
import streamlit as st
from datetime import datetime, timedelta
from uuid import uuid4

# --------------- 初始化全局状态 ---------------
# 初始化API客户端
if "api_client" not in st.session_state:
    from api_client import APIClient
    st.session_state.api_client = APIClient()

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
    st.session_state.api_connected = st.session_state.api_client.check_health()

# 确保当前对话的消息列表存在
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
if "messages" not in current_conv:
    current_conv["messages"] = []

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

    # 2. 旅行偏好设置（将发送给后端）
    st.header("🎯 旅行偏好")
    budget = st.number_input(
        "预算 (USD)",
        min_value=0,
        value=st.session_state.budget,
        step=100,
        key="travel_budget"
    )
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
    
    # 打包旅行偏好为字典
    travel_preferences = {
        "budget": budget,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "language": language
    }
    st.divider()

    # 3. 订单记录展示
    st.header("📋 所有订单")
    if st.session_state.orders:
        for order in st.session_state.orders:
            st.write(f"• {order['item']} - ${order['price']}")
            st.caption(f"时间: {order['time']} | 状态: {order['status']}")
        total_spent = sum(o['price'] for o in st.session_state.orders)
        st.write(f"**总消费**: ${total_spent}")
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
        if st.button("🔄 刷新"):
            st.session_state.api_connected = st.session_state.api_client.check_health()
            st.rerun()
    if not st.session_state.api_connected:
        st.info("请启动后端服务：`python backend/app.py`")

# --------------- 聊天内容展示与交互 ---------------
# 获取当前对话的消息列表
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
messages = current_conv["messages"]

# 显示历史消息
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 处理用户输入
if prompt := st.chat_input("请输入您的旅行需求...（例如：帮我订东京三晚的酒店）"):
        # 添加用户消息到当前对话
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("处理中..."):
            # 后端未连接时的处理
            if not st.session_state.api_connected:
                error_msg = "后端未连接，请先启动后端服务再使用功能"
                st.error(error_msg)
                messages.append({"role": "assistant", "content": error_msg})
                st.rerun()

            # 后端已连接时的处理
            else:
                # 计算剩余预算
                total_spent = sum(o['price'] for o in st.session_state.orders)
                remaining_budget = budget - total_spent
                travel_preferences["budget"] = remaining_budget  # 更新为剩余预算

                # 发送用户需求和旅行偏好给后端
                backend_response = st.session_state.api_client.chat(
                    prompt=prompt,
                    preferences=travel_preferences
                )

                # 处理后端无响应的情况
                if not backend_response:
                    no_response_msg = "未收到后端响应，请稍后再试"
                    st.error(no_response_msg)
                    messages.append({"role": "assistant", "content": no_response_msg})
                    st.rerun()

                # 处理后端响应
                action = backend_response.get("action")
                params = backend_response.get("params", {})

                # 直接回复
                if action == "reply":
                    reply_content = backend_response.get("content", "已收到您的需求")
                    st.markdown(reply_content)
                    messages.append({"role": "assistant", "content": reply_content})

                # 搜索酒店
                elif action == "search_hotels":
                    hotels = st.session_state.api_client.search_hotels(
                        city=params.get("city", ""),
                        check_in=params.get("check_in", travel_preferences["start_date"]),
                        check_out=params.get("check_out", travel_preferences["end_date"]),
                        budget=remaining_budget
                    )

                    if not hotels or "hotels" not in hotels:
                        no_hotel_msg = "未找到符合条件的酒店"
                        st.error(no_hotel_msg)
                        messages.append({"role": "assistant", "content": no_hotel_msg})
                    else:
                        '''调用展示函数'''
                        pass


                        # hotel_list_msg = "为您找到以下酒店：\n\n"
                        # for i, hotel in enumerate(hotels["hotels"]):
                        #     hotel_list_msg += f"{i+1}. **{hotel['name']}**\n"
                        #     hotel_list_msg += f"   价格：${hotel['price']}/晚 | 评分：{hotel.get('rating', '暂无')}\n"
                        #     hotel_list_msg += f"   地址：{hotel['address']}\n"
                        #     hotel_list_msg += f"   设施：{', '.join(hotel.get('amenities', ['无']))[:50]}...\n\n"
                        # hotel_list_msg += "请回复酒店编号（如1、2）完成预订，或告诉我您的其他需求"
                        # st.markdown(hotel_list_msg)
                        # messages.append({
                        #     "role": "assistant",
                        #     "content": hotel_list_msg,
                        #     "attached_hotels": hotels["hotels"]
                        # })

                # 搜索航班
                elif action == "search_flights":
                    # 获取航班ID列表
                    flight_ids = st.session_state.api_client.search_flights(
                        origin=params.get("origin", ""),
                        destination=params.get("destination", ""),
                        date=params.get("date", travel_preferences["start_date"]),
                        adults=params.get("adults", 1),
                        travel_class=params.get("travel_class", "ECONOMY")
                    )

                    if not flight_ids:
                        no_flight_msg = "未找到符合条件的航班"
                        st.error(no_flight_msg)
                        messages.append({"role": "assistant", "content": no_flight_msg})
                    else:
                        # 获取并展示每个航班的详情
                        flight_list_msg = "为您找到以下航班：\n\n"
                        attached_flights = []
                        
                        for i, flight_id in enumerate(flight_ids[:10]):  # 限制最多显示5个结果
                            flight = st.session_state.api_client.get_flight_details(flight_id)
                            if not flight:
                                continue
                            pass
                                
                            # attached_flights.append(flight)
                            # flight_list_msg += f"{i+1}. **{flight['carrier']} {flight['flight_number']}**\n"
                            # flight_list_msg += f"   出发：{flight['departure']['iata']} {flight['departure']['time']}\n"
                            # flight_list_msg += f"   到达：{flight['arrival']['iata']} {flight['arrival']['time']}\n"
                            # flight_list_msg += f"   时长：{flight['duration']}分钟 | 舱位：{flight['cabin_class']}\n"
                            # flight_list_msg += f"   价格：{flight['price']} {flight['currency']}\n\n"
                            
                        if not attached_flights:
                            no_details_msg = "无法获取航班详情"
                            st.error(no_details_msg)
                            messages.append({"role": "assistant", "content": no_details_msg})
                        else:
                            flight_list_msg += "请回复航班编号（如1、2）完成预订，或告诉我您的其他需求"
                            st.markdown(flight_list_msg)
                            messages.append({
                                "role": "assistant",
                                "content": flight_list_msg,
                                "attached_flights": attached_flights
                            })

                # 未知指令处理
                else:
                    default_msg = "已收到您的需求，正在处理中..."
                    st.markdown(default_msg)
                    messages.append({"role": "assistant", "content": default_msg})
























    # 添加用户消息到当前对话
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("处理中..."):
            # 后端未连接时的处理（提前终止逻辑）
            if not st.session_state.api_connected:
                error_msg = "后端未连接，请先启动后端服务再使用功能"
                st.error(error_msg)
                messages.append({"role": "assistant", "content": error_msg})
                pass

            # 后端已连接时的处理
            else:
                #if len(order)>order_count:
                    # total_spent = sum(order["price"] for order in st.session_state.orders)
                    # remaining_budget = st.session_state.budget - total_spent
                    # travel_preferences = {
                    #     "budget": remaining_budget,
                    #     "start_date": start_date.strftime("%Y-%m-%d"),
                    #     "end_date": end_date.strftime("%Y-%m-%d"),
                    #     "language": language
                    # }


                # 1. 发送用户需求和旅行偏好给后端
                backend_response = st.session_state.api_client.chat(
                    prompt=prompt,
                    preferences=travel_preferences
                )

                # 2. 处理后端无响应的情况
                if not backend_response:
                    no_response_msg = "未收到后端响应，请稍后再试"
                    st.error(no_response_msg)
                    messages.append({"role": "assistant", "content": no_response_msg})
                    pass

                # 3. 处理后端响应
                else:
                    action = backend_response.get("action")
                    params = backend_response.get("params", {})

                    # 3.1 后端直接返回文本回复
                    if action == "reply":
                        reply_content = backend_response.get("content", "已收到您的需求")
                        st.markdown(reply_content)
                        messages.append({"role": "assistant", "content": reply_content})

                    # 3.2 后端指令：搜索酒店
                    elif action == "search_hotels":
                        # 调用酒店搜索接口
                        hotels = st.session_state.api_client.search_hotels(
                            city=params.get("city", ""),
                            check_in=params.get("check_in", ""),
                            check_out=params.get("check_out", ""),
                            budget=travel_preferences["budget"]
                        )

                        # 处理搜索结果
                        if not hotels or "hotels" not in hotels:
                            no_hotel_msg = "未找到符合条件的酒店"
                            st.error(no_hotel_msg)
                            messages.append({"role": "assistant", "content": no_hotel_msg})
                        else:
                            # 展示酒店列表
                            hotel_list_msg = "为您找到以下酒店：\n\n"
                            for i, hotel in enumerate(hotels["hotels"]):
                                hotel_list_msg += f"{i+1}. **{hotel['name']}**\n"
                                hotel_list_msg += f"   价格：${hotel['price']}/晚\n"
                                hotel_list_msg += f"   地址：{hotel['address']}\n"
                                hotel_list_msg += f"   描述：{hotel['desc']}\n\n"
                            hotel_list_msg += "请回复酒店编号（如1、2）完成预订"
                            st.markdown(hotel_list_msg)
                            # 暂存酒店信息用于后续预订
                            messages.append({
                                "role": "assistant",
                                "content": hotel_list_msg,
                                "attached_hotels": hotels["hotels"]
                            })

                    # 3.3 后端指令：确认预订
                    elif action == "book_hotel":
                        # 调用酒店预订接口
                        booking_result = st.session_state.api_client.book_hotel(
                            hotel_id=params.get("hotel_id", ""),
                            trip_id=st.session_state.trips[0]["id"]
                        )

                        # 处理预订结果
                        if booking_result and booking_result.get("status") == "success":
                            order_id = str(uuid4())[:8]
                            st.session_state.orders.append({
                                "id": order_id,
                                "item": booking_result["hotel_name"],
                                "price": booking_result["price"],
                                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "trip_id": st.session_state.trips[0]["id"],
                                "status": "已预订"
                            })
                            success_msg = f"预订成功！订单号：{order_id}\n酒店：{booking_result['hotel_name']}\n总价：${booking_result['price']}"
                            st.success(success_msg)
                            messages.append({"role": "assistant", "content": success_msg})
                        else:
                            fail_msg = "预订失败，请重试"
                            st.error(fail_msg)
                            messages.append({"role": "assistant", "content": fail_msg})

                    # 3.4 未知指令处理
                    else:
                        default_msg = "已收到您的需求，正在处理中..."
                        st.markdown(default_msg)
                        messages.append({"role": "assistant", "content": default_msg})







