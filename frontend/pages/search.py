import streamlit as st
from datetime import datetime, timedelta
from uuid import uuid4
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.hotel_card import display_hotel_card, display_hotel_filters
from components.weather_widget import display_weather_compact, get_mock_weather_data
from components.flight_card import display_flight_card, display_flight_details_modal

# ========== 页面配置 ==========
st.set_page_config(
    page_title="搜索 | 旅行助手",
    page_icon="🔍",
    layout="wide"
)

# ========== 初始化状态 ==========
if "search_results" not in st.session_state:
    st.session_state.search_results = {
        "flights": [],
        "hotels": [],
        "attractions": []
    }

if "current_payment" not in st.session_state:
    st.session_state.current_payment = None

if "search_params" not in st.session_state:
    st.session_state.search_params = {}

if "trips" not in st.session_state:
    st.session_state.trips = [{
        "id": "trip_default",
        "name": "默认行程",
        "destination": "Tokyo",
        "start_date": datetime.now().strftime("%Y-%m-%d"),
        "end_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    }]

if "budget" not in st.session_state:
    st.session_state.budget = 5000

if "orders" not in st.session_state:
    st.session_state.orders = []

if "show_flight_details" not in st.session_state:
    st.session_state.show_flight_details = None

# ========== 支付模态弹窗 ==========
@st.dialog("💳 支付确认", width="large")
def payment_dialog(trip_id, item_name, price, item_id):
    """
    支付确认对话框
    
    参数:
        trip_id: 行程ID
        item_name: 商品名称
        price: 价格
        item_id: 商品ID
    """
    
    # 计算预算
    total_spent = sum(o['price'] for o in st.session_state.orders if o.get('trip_id') == trip_id)
    remaining = st.session_state.budget - total_spent
    
    # 订单信息卡片
    st.markdown("""
    <style>
    .payment-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin-bottom: 20px;
    }
    .payment-item {
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
    }
    .payment-price {
        font-size: 32px;
        font-weight: bold;
        margin: 10px 0;
    }
    .payment-budget {
        background: rgba(255,255,255,0.2);
        padding: 12px;
        border-radius: 8px;
        margin-top: 12px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class='payment-card'>
        <div class='payment-item'>📦 {item_name}</div>
        <div class='payment-price'>💰 ${price:.2f}</div>
        <div class='payment-budget'>
            <div style='display: flex; justify-content: space-between;'>
                <span>剩余预算: <strong>${remaining:.2f}</strong></span>
                <span>支付后: <strong>${remaining - price:.2f}</strong></span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 预算警告
    if price > remaining:
        st.error("❌ 预算不足！请调整预算或选择其他商品。")
        if st.button("关闭", type="secondary", use_container_width=True):
            st.session_state.current_payment = None
            st.rerun()
        return
    elif price > remaining * 0.8:
        st.warning("⚠️ 此次支付将使用超过80%的剩余预算")
    
    st.divider()
    
    # 支付表单
    st.subheader("🔐 支付信息")
    
    with st.form("payment_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            card_number = st.text_input(
                "卡号",
                value="1234 5678 9012 3456",
                placeholder="1234 5678 9012 3456",
                help="测试卡号: 1234 5678 9012 3456"
            )
            
            card_name = st.text_input(
                "持卡人姓名",
                value="Test User",
                placeholder="ZHANG SAN"
            )
        
        with col2:
            col_a, col_b = st.columns(2)
            with col_a:
                expiry = st.text_input(
                    "有效期",
                    value="12/25",
                    placeholder="MM/YY"
                )
            with col_b:
                cvv = st.text_input(
                    "CVV",
                    value="123",
                    type="password",
                    max_chars=3,
                    placeholder="123"
                )
            
            password = st.text_input(
                "支付密码",
                type="password",
                placeholder="测试密码: 1234",
                help="测试密码: 1234"
            )
        
        st.divider()
        
        # 提交按钮
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            submit = st.form_submit_button(
                "✅ 确认支付",
                type="primary",
                use_container_width=True
            )
        
        with col_btn2:
            cancel = st.form_submit_button(
                "❌ 取消",
                use_container_width=True
            )
        
        # 处理支付
        if submit:
            if password == "1234":
                # 创建订单
                order_id = str(uuid4())[:8].upper()
                st.session_state.orders.append({
                    "id": order_id,
                    "item": item_name,
                    "price": price,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "trip_id": trip_id,
                    "status": "已支付"
                })
                
                # 清除支付状态
                st.session_state.current_payment = None
                
                # 显示成功消息
                st.success(f"✅ 支付成功！订单号: {order_id}")
                st.balloons()
                
                # 延迟后关闭对话框
                import time
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("❌ 支付密码错误！请输入正确的密码（测试: 1234）")
        
        if cancel:
            st.session_state.current_payment = None
            st.rerun()

# ========== 航班详情模态弹窗 ==========
@st.dialog("✈️ 航班详细信息", width="large")
def flight_details_dialog(flight_data):
    """
    航班详情对话框
    
    参数:
        flight_data (dict): 航班数据
    """
    
    amenities_data = flight_data.get('amenities', [])
    
    # 基本信息
    st.markdown("### 📌 基本信息")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("航班号", f"{flight_data.get('carrier_code', 'XX')} {flight_data.get('flight_number', '000')}")
    with col2:
        st.metric("机型", flight_data.get('aircraft_code', 'N/A'))
    with col3:
        st.metric("可订座位", flight_data.get('number_of_bookable_seats', 0))
    
    st.divider()
    
    # 航班时刻
    st.markdown("### 🕐 航班时刻")
    col_a, col_b = st.columns(2)
    
    with col_a:
        departure_time = flight_data.get('departure_time', 'N/A')
        try:
            dep_dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
            dep_display = dep_dt.strftime("%Y-%m-%d %H:%M")
        except:
            dep_display = departure_time
        
        st.info(f"🛫 **出发**: {dep_display}\n\n📍 {flight_data.get('departure_iata', 'XXX')}")
    
    with col_b:
        arrival_time = flight_data.get('arrival_time', 'N/A')
        try:
            arr_dt = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
            arr_display = arr_dt.strftime("%Y-%m-%d %H:%M")
        except:
            arr_display = arrival_time
        
        st.success(f"🛬 **到达**: {arr_display}\n\n📍 {flight_data.get('arrival_iata', 'XXX')}")
    
    st.caption(f"⏱️ 飞行时间: {flight_data.get('duration', 'N/A')}")
    
    st.divider()
    
    # 舱位与行李
    st.markdown("### 🧳 舱位与行李")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        cabin_class = flight_data.get('cabin_class', 'ECONOMY')
        cabin_display = {
            'ECONOMY': '经济舱',
            'PREMIUM_ECONOMY': '超级经济舱',
            'BUSINESS': '商务舱',
            'FIRST': '头等舱'
        }.get(cabin_class, cabin_class)
        
        st.write(f"**舱位**: {cabin_display}")
        st.write(f"**运营商**: {flight_data.get('operating_carrier', 'N/A')}")
        st.write(f"**票价代码**: {flight_data.get('fare_basis', 'N/A')}")
    
    with col_y:
        checked_bags = flight_data.get('included_checked_bags', 'N/A')
        cabin_bags = flight_data.get('included_cabin_bags', 'N/A')
        
        st.write(f"**托运行李**: {checked_bags}")
        st.write(f"**手提行李**: {cabin_bags}")
        st.write(f"**出票截止**: {flight_data.get('last_ticketing_date', 'N/A')}")
    
    st.divider()
    
    # 附加服务
    st.markdown("### 🎁 附加服务 & 便利设施")
    
    if amenities_data and len(amenities_data) > 0:
        # 使用表格显示
        import pandas as pd
        
        df_amenities = pd.DataFrame(amenities_data)
        df_amenities['费用'] = df_amenities['is_chargeable'].apply(lambda x: '💰 收费' if x else '✅ 免费')
        df_amenities = df_amenities[['service', '费用']]
        df_amenities.columns = ['服务项目', '费用']
        
        st.dataframe(
            df_amenities,
            use_container_width=True,
            hide_index=True,
            column_config={
                "服务项目": st.column_config.TextColumn("服务项目", width="large"),
                "费用": st.column_config.TextColumn("费用", width="small")
            }
        )
    else:
        st.info("暂无附加服务信息")
    
    st.divider()
    
    # 价格明细
    st.markdown("### 💰 价格明细")
    
    col_price1, col_price2, col_price3 = st.columns(3)
    
    with col_price1:
        st.metric("基础票价", f"${flight_data.get('base_price', 0):.2f}")
    
    with col_price2:
        tax = flight_data.get('total_price', 0) - flight_data.get('base_price', 0)
        st.metric("税费", f"${tax:.2f}")
    
    with col_price3:
        st.metric(
            "总价",
            f"{flight_data.get('currency', 'USD')} ${flight_data.get('grand_total', 0):.2f}",
            delta=None
        )
    
    st.divider()
    
    # 关闭按钮
    if st.button("关闭", use_container_width=True, type="secondary"):
        st.session_state.show_flight_details = None
        st.rerun()

# ========== 页面标题 ==========
st.title("🔍 搜索旅行服务")
st.caption("搜索航班、酒店、景点门票，规划完美旅程")

# ========== 侧边栏 ==========
with st.sidebar:
    st.header("🎯 搜索类别")
    
    # 搜索类别选择
    search_category = st.radio(
        "选择服务类型",
        ["✈️ 航班", "🏨 酒店", "🎫 景点门票"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # 💰 预算状态
    st.header("💰 预算状态")
    total_spent = sum(o['price'] for o in st.session_state.orders)
    remaining = st.session_state.budget - total_spent
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("总预算", f"${st.session_state.budget}")
    with col2:
        st.metric("剩余", f"${remaining}")
    
    # 预算进度条
    progress = min(total_spent / st.session_state.budget, 1.0) if st.session_state.budget > 0 else 0
    st.progress(progress)
    
    if progress > 0.9:
        st.warning("⚠️ 预算即将用完")
    
    st.divider()
    
    # 📜 最近搜索
    st.header("📜 最近搜索")
    if st.session_state.search_params:
        for key, value in st.session_state.search_params.items():
            st.caption(f"{key}: {value}")
    else:
        st.info("暂无搜索历史")
    
    st.divider()
    
    # 🌤️ 目的地天气
    st.header("🌤️ 目的地天气")
    
    if st.session_state.search_params:
        city = st.session_state.search_params.get('city', 'Tokyo')
    else:
        city = st.text_input("城市", "Tokyo", key="sidebar_weather_city")
    
    current_weather = get_mock_weather_data(city)
    display_weather_compact(current_weather, city, forecast_days=4)

# ========== 主内容区 ==========

# ✈️ 航班搜索
if search_category == "✈️ 航班":
    with st.container(border=True):
        st.subheader("✈️ 搜索航班")
        
        col1, col2 = st.columns(2)
        with col1:
            origin = st.text_input("出发地（IATA代码）", "HKG", key="flight_origin")
        with col2:
            destination = st.text_input("目的地（IATA代码）", "NRT", key="flight_dest")
        
        col3, col4 = st.columns(2)
        with col3:
            departure_date = st.date_input("出发日期", datetime.now(), key="flight_depart")
        with col4:
            return_date = st.date_input("返程日期（可选）", None, key="flight_return")
        
        with st.expander("🔧 高级选项", expanded=False):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                passengers = st.number_input("乘客数", 1, 10, 1, key="flight_pass")
            with col_b:
                cabin_class = st.selectbox(
                    "舱位", 
                    ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"], 
                    format_func=lambda x: {"ECONOMY": "经济舱", "PREMIUM_ECONOMY": "超经舱", "BUSINESS": "商务舱", "FIRST": "头等舱"}[x],
                    key="flight_class"
                )
            with col_c:
                direct_only = st.checkbox("仅直飞", key="flight_direct")
        
        if st.button("🔍 搜索航班", type="primary", use_container_width=True):
            with st.spinner("🔄 正在搜索航班..."):
                st.session_state.search_params = {
                    "city": destination,
                    "origin": origin,
                    "destination": destination,
                    "departure_date": departure_date.strftime("%Y-%m-%d"),
                    "passengers": passengers,
                    "cabin_class": cabin_class
                }
                
                st.session_state.search_results["flights"] = [
                    {
                        "id": "FL001",
                        "departure_iata": origin,
                        "arrival_iata": destination,
                        "departure_time": f"{departure_date}T08:30:00Z",
                        "arrival_time": f"{departure_date}T14:15:00Z",
                        "carrier_code": "CA",
                        "flight_number": "123",
                        "aircraft_code": "Boeing 777",
                        "operating_carrier": "China Airlines",
                        "duration": "5h 45m",
                        "currency": "USD",
                        "total_price": 450.00,
                        "base_price": 380.00,
                        "grand_total": 450.00,
                        "cabin_class": cabin_class,
                        "number_of_bookable_seats": 12,
                        "included_checked_bags": "1 件 23kg",
                        "included_cabin_bags": "1 件 7kg",
                        "last_ticketing_date": "2025-11-20",
                        "fare_basis": "YLOW",
                        "amenities": [
                            {"service": "机上WiFi", "is_chargeable": True},
                            {"service": "餐食", "is_chargeable": False},
                            {"service": "娱乐系统", "is_chargeable": False},
                            {"service": "毛毯枕头", "is_chargeable": False}
                        ]
                    },
                    {
                        "id": "FL002",
                        "departure_iata": origin,
                        "arrival_iata": destination,
                        "departure_time": f"{departure_date}T13:00:00Z",
                        "arrival_time": f"{departure_date}T18:50:00Z",
                        "carrier_code": "NH",
                        "flight_number": "456",
                        "aircraft_code": "Airbus A350",
                        "operating_carrier": "ANA",
                        "duration": "5h 50m",
                        "currency": "USD",
                        "total_price": 520.00,
                        "base_price": 450.00,
                        "grand_total": 520.00,
                        "cabin_class": cabin_class,
                        "number_of_bookable_seats": 8,
                        "included_checked_bags": "2 件 23kg",
                        "included_cabin_bags": "1 件 10kg",
                        "last_ticketing_date": "2025-11-22",
                        "fare_basis": "YHIGH",
                        "amenities": [
                            {"service": "机上WiFi", "is_chargeable": False},
                            {"service": "餐食", "is_chargeable": False},
                            {"service": "娱乐系统", "is_chargeable": False},
                            {"service": "优先登机", "is_chargeable": False}
                        ]
                    }
                ]
                
                st.success(f"✅ 找到 {len(st.session_state.search_results['flights'])} 个航班")
                st.rerun()
    
    st.divider()
    
    # 显示航班搜索结果
    if st.session_state.search_results["flights"]:
        st.subheader("✈️ 搜索结果")
        st.caption(f"显示 {len(st.session_state.search_results['flights'])} 个航班")
        
        sort_option = st.selectbox(
            "排序方式",
            ["价格从低到高", "价格从高到低", "出发时间最早", "飞行时间最短"],
            key="flight_sort"
        )
        
        flights = st.session_state.search_results["flights"].copy()
        
        if sort_option == "价格从低到高":
            flights.sort(key=lambda x: x['total_price'])
        elif sort_option == "价格从高到低":
            flights.sort(key=lambda x: x['total_price'], reverse=True)
        elif sort_option == "出发时间最早":
            flights.sort(key=lambda x: x['departure_time'])
        
        for flight in flights:
            action = display_flight_card(flight, key_prefix=f"search_flight_{flight['id']}")
            
            if action == "book":
                default_trip_id = st.session_state.trips[0]["id"]
                st.session_state.current_payment = (
                    default_trip_id,
                    f"{flight['carrier_code']}{flight['flight_number']} {flight['departure_iata']}→{flight['arrival_iata']}",
                    flight['total_price'],
                    f"flight_{flight['id']}"
                )
                # 触发支付弹窗
                payment_dialog(*st.session_state.current_payment)
            
            elif action == "details":
                # 触发详情弹窗
                flight_details_dialog(flight)

# 🏨 酒店搜索
elif search_category == "🏨 酒店":
    with st.container(border=True):
        st.subheader("🏨 搜索酒店")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            city = st.text_input("目的地城市", "Tokyo", key="hotel_city")
        with col2:
            check_in = st.date_input("入住日期", datetime.now(), key="hotel_checkin")
        with col3:
            check_out = st.date_input("退房日期", datetime.now() + timedelta(days=2), key="hotel_checkout")
        
        with st.expander("🔧 高级选项", expanded=False):
            col_a, col_b = st.columns(2)
            with col_a:
                guests = st.number_input("入住人数", 1, 10, 1, key="hotel_guests")
            with col_b:
                rooms = st.number_input("房间数量", 1, 5, 1, key="hotel_rooms")
        
        if st.button("🔍 搜索酒店", type="primary", use_container_width=True, key="search_hotels_btn"):
            with st.spinner("🔄 正在搜索酒店..."):
                st.session_state.search_params = {
                    "city": city,
                    "check_in": check_in.strftime("%Y-%m-%d"),
                    "check_out": check_out.strftime("%Y-%m-%d"),
                    "guests": guests,
                    "rooms": rooms
                }
                
                nights = (check_out - check_in).days
                st.session_state.search_results["hotels"] = [
                    {
                        "id": 1,
                        "name": f"{city} Central Hotel",
                        "price": 150,
                        "total_price": 150 * nights,
                        "nights": nights,
                        "desc": "位于市中心，步行可达主要景点，含早餐",
                        "rating": 4.5,
                        "location": f"{city}市中心",
                        "amenities": ["免费WiFi", "早餐", "停车场", "健身房"]
                    },
                    {
                        "id": 2,
                        "name": f"{city} Bay Resort",
                        "price": 180,
                        "total_price": 180 * nights,
                        "nights": nights,
                        "desc": "海景房，含机场接送和晚餐",
                        "rating": 4.7,
                        "location": f"{city}海湾区",
                        "amenities": ["游泳池", "早餐", "机场接送", "海景"]
                    }
                ]
                
                st.success(f"✅ 找到 {len(st.session_state.search_results['hotels'])} 家酒店")
                st.rerun()
    
    st.divider()
    
    if st.session_state.search_results["hotels"]:
        st.subheader("🎛️ 筛选条件")
        filters = display_hotel_filters()
        
        st.divider()
        
        st.subheader("🏨 搜索结果")
        
        filtered_hotels = [
            h for h in st.session_state.search_results["hotels"]
            if filters['price_range'][0] <= h['price'] <= filters['price_range'][1]
            and h['rating'] >= filters['min_rating']
        ]
        
        st.caption(f"显示 {len(filtered_hotels)} / {len(st.session_state.search_results['hotels'])} 家酒店")
        
        sort_option = st.selectbox(
            "排序方式",
            ["价格从低到高", "价格从高到低", "评分最高"],
            key="hotel_sort"
        )
        
        if sort_option == "价格从低到高":
            filtered_hotels.sort(key=lambda x: x['price'])
        elif sort_option == "价格从高到低":
            filtered_hotels.sort(key=lambda x: x['price'], reverse=True)
        elif sort_option == "评分最高":
            filtered_hotels.sort(key=lambda x: x['rating'], reverse=True)
        
        for hotel in filtered_hotels:
            action = display_hotel_card(hotel, key_prefix=f"search_hotel_{hotel['id']}")
            
            if action == "book":
                default_trip_id = st.session_state.trips[0]["id"]
                st.session_state.current_payment = (
                    default_trip_id,
                    f"{hotel['name']} ({hotel['nights']}晚)",
                    hotel['total_price'],
                    f"hotel_{hotel['id']}"
                )
                # 触发支付弹窗
                payment_dialog(*st.session_state.current_payment)

# 🎫 景点门票搜索
elif search_category == "🎫 景点门票":
    with st.container(border=True):
        st.subheader("🎫 搜索景点门票")
        
        col1, col2 = st.columns(2)
        with col1:
            attraction_city = st.text_input("目的地", "Tokyo", key="attr_city")
        with col2:
            visit_date = st.date_input("游玩日期", datetime.now(), key="attr_date")
        
        with st.expander("🔧 筛选条件", expanded=False):
            categories = st.multiselect(
                "景点类型",
                ["历史文化", "自然风光", "主题乐园", "博物馆", "美食体验"],
                key="attr_categories"
            )
        
        if st.button("🔍 搜索景点", type="primary", use_container_width=True):
            st.info("🚧 景点门票搜索功能开发中，敬请期待...")