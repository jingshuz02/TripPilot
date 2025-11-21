"""
仿真机票卡片组件 - 统一预算版
特点:
1. 清晰显示起飞地 → 目的地
2. 舱位选择(经济舱、商务舱、头等舱)
3. 💰 统一预算检查
4. ✅ 预订成功弹窗
5. 浅绿色配色
"""

import streamlit as st
from datetime import datetime


def get_remaining_budget():
    """获取剩余预算 - 与chat.py保持一致"""
    if "current_trip" in st.session_state and "total_spent" in st.session_state:
        total_budget = st.session_state.current_trip.get("budget", 5000)
        return total_budget - st.session_state.total_spent
    return 0


def display_flight_card_v2(flight, key_prefix="flight", message_id=0, on_book_callback=None):
    """
    仿真机票卡片展示 - 带统一预算检查

    参数:
        flight: 航班数据字典
        key_prefix: 按钮key前缀
        message_id: 消息ID
        on_book_callback: 预订回调函数
    """

    st.markdown("""
    <style>
    .flight-card-realistic {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
        position: relative;
        z-index: 1;
    }
    
    .flight-card-realistic:hover {
        border-color: #10b981;
        box-shadow: 0 4px 12px rgba(10, 185, 129, 0.15);
    }
    
    .flight-route-display {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        padding: 16px;
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
        border-radius: 10px;
    }
    
    .flight-city-info {
        flex: 1;
        text-align: center;
    }
    
    .flight-city-code {
        font-size: 28px;
        font-weight: 800;
        color: #047857;
        margin-bottom: 4px;
    }
    
    .flight-city-name {
        font-size: 13px;
        color: #6b7280;
    }
    
    .flight-arrow {
        font-size: 32px;
        color: #10b981;
        margin: 0 16px;
    }
    
    .flight-basic-info {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .flight-info-item {
        text-align: center;
        padding: 8px;
    }
    
    .flight-info-label {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }
    
    .flight-info-value {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
    }
    
    .flight-airline-badge {
        display: inline-flex;
        align-items: center;
        background: #f3f4f6;
        color: #374151;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        margin-right: 8px;
    }
    
    .flight-price-display {
        font-size: 28px;
        font-weight: 700;
        color: #10b981;
        line-height: 1;
    }
    
    .flight-cabin-notice {
        font-size: 12px;
        color: #6b7280;
        margin-top: 4px;
    }
    
    .budget-warning-flight {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #92400e;
        margin-top: 8px;
    }
    
    .budget-ok-flight {
        background: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #065f46;
        margin-top: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

    flight_id = flight.get('id', 0)
    details_key = f"{key_prefix}_detail_{message_id}_{flight_id}"
    cabin_key = f"{key_prefix}_cabin_{message_id}_{flight_id}"
    book_key = f"{key_prefix}_book_{message_id}_{flight_id}"

    if details_key not in st.session_state:
        st.session_state[details_key] = False

    if cabin_key not in st.session_state:
        st.session_state[cabin_key] = "economy"

    # 舱位价格配置
    base_price = flight.get('price', flight.get('total_price', 0))
    cabin_prices = {
        "economy": {"name": "经济舱", "price": base_price, "multiplier": 1.0},
        "business": {"name": "商务舱", "price": int(base_price * 2.5), "multiplier": 2.5},
        "first": {"name": "头等舱", "price": int(base_price * 4.0), "multiplier": 4.0}
    }

    # ✅ 获取剩余预算
    remaining_budget = get_remaining_budget()

    with st.container():
        st.markdown("<div class='flight-card-realistic'>", unsafe_allow_html=True)

        # 航线显示
        origin = flight.get('origin', '出发地')
        destination = flight.get('destination', '目的地')

        origin_code = origin[:3].upper() if len(origin) <= 4 else origin[:3].upper()
        dest_code = destination[:3].upper() if len(destination) <= 4 else destination[:3].upper()

        st.markdown(f"""
        <div class='flight-route-display'>
            <div class='flight-city-info'>
                <div class='flight-city-code'>{origin_code}</div>
                <div class='flight-city-name'>{origin}</div>
            </div>
            <div class='flight-arrow'>✈</div>
            <div class='flight-city-info'>
                <div class='flight-city-code'>{dest_code}</div>
                <div class='flight-city-name'>{destination}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 基本信息
        carrier_name = flight.get('carrier_name', flight.get('carrier_code', '航空公司'))
        flight_number = flight.get('flight_number', 'XXXX')
        departure_time = flight.get('departure_time', 'N/A')
        arrival_time = flight.get('arrival_time', 'N/A')
        duration = flight.get('duration', 'N/A')
        departure_date = flight.get('departure_date', datetime.now().strftime('%Y-%m-%d'))

        col_airline, col_date = st.columns([2, 1])

        with col_airline:
            st.markdown(f"""
                <span class='flight-airline-badge'>{carrier_name} {flight_number}</span>
            """, unsafe_allow_html=True)

        with col_date:
            st.markdown(f"""
                <div style='text-align: right; font-size: 13px; color: #6b7280;'>
                    {departure_date}
                </div>
            """, unsafe_allow_html=True)

        # 时间信息卡片
        st.markdown(f"""
        <div class='flight-basic-info'>
            <div class='flight-info-item'>
                <div class='flight-info-label'>起飞时间</div>
                <div class='flight-info-value'>{departure_time}</div>
            </div>
            <div class='flight-info-item'>
                <div class='flight-info-label'>飞行时长</div>
                <div class='flight-info-value'>{duration}</div>
            </div>
            <div class='flight-info-item'>
                <div class='flight-info-label'>到达时间</div>
                <div class='flight-info-value'>{arrival_time}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 舱位选择和价格显示
        col_cabin, col_price, col_btn = st.columns([2, 1.5, 1.5])

        with col_cabin:
            st.markdown("**选择舱位**")
            selected_cabin = st.selectbox(
                "舱位",
                options=list(cabin_prices.keys()),
                format_func=lambda x: cabin_prices[x]["name"],
                key=cabin_key,
                label_visibility="collapsed"
            )

            cabin_info = {
                "economy": "标准座椅 • 20kg行李",
                "business": "平躺座椅 • 30kg行李 • 贵宾休息室",
                "first": "豪华座椅 • 40kg行李 • 专属服务"
            }
            st.caption(cabin_info[selected_cabin])

        with col_price:
            current_price = cabin_prices[selected_cabin]["price"]
            st.markdown(f"""
                <div style='text-align: right; padding-top: 8px;'>
                    <div class='flight-price-display'>¥{current_price:,}</div>
                    <div class='flight-cabin-notice'>{cabin_prices[selected_cabin]["name"]}</div>
                </div>
            """, unsafe_allow_html=True)

        with col_btn:
            st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)

            button_text = "收起详情" if st.session_state[details_key] else "查看详情"
            if st.button(
                button_text,
                key=details_key + "_btn",
                use_container_width=True
            ):
                st.session_state[details_key] = not st.session_state[details_key]
                st.rerun()

            # ✅ 预订按钮 - 带预算检查
            can_afford = current_price <= remaining_budget

            if can_afford:
                if st.button(
                    "预订",
                    key=book_key,
                    type="primary",
                    use_container_width=True
                ):
                    if on_book_callback:
                        # 准备航班数据(包含选中的舱位)
                        flight_data = flight.copy()
                        flight_data['cabin_class'] = cabin_prices[selected_cabin]["name"]
                        flight_data['price'] = current_price

                        on_book_callback("flight", flight_data, current_price)
                        st.rerun()
                    else:
                        # 默认行为
                        st.session_state.total_spent = st.session_state.get("total_spent", 0) + current_price
                        st.success(f"""
                        ✅ 预订成功!
                        
                        - 航班: {carrier_name} {flight_number}
                        - 舱位: {cabin_prices[selected_cabin]['name']}
                        - 价格: ¥{current_price:,}
                        - 剩余预算: ¥{get_remaining_budget():,}
                        """)
                        st.balloons()
                        st.rerun()
            else:
                st.button(
                    "预算不足",
                    key=book_key,
                    disabled=True,
                    use_container_width=True
                )

        # ✅ 预算提示
        if not can_afford:
            st.markdown(f"""
                <div class='budget-warning-flight'>
                    💰 预算不足 | 需要: ¥{current_price:,} | 剩余: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='budget-ok-flight'>
                    ✅ 预算充足 | 剩余: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)

        # 详情展开区域
        if st.session_state[details_key]:
            st.markdown("""
            <div style='background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; 
                        padding: 16px; margin-top: 12px;'>
            """, unsafe_allow_html=True)

            aircraft = flight.get('aircraft', '波音737')
            stops = flight.get('stops', 0)
            available_seats = flight.get('available_seats', 20)

            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                        border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>航班号</span>
                <span style='color: #111827; font-weight: 600;'>{carrier_name} {flight_number}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                        border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>机型</span>
                <span style='color: #111827; font-weight: 600;'>{aircraft}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                        border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>经停</span>
                <span style='color: #111827; font-weight: 600;'>{'直飞' if stops == 0 else f'{stops}次经停'}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>剩余座位</span>
                <span style='color: #111827; font-weight: 600;'>{available_seats}个</span>
            </div>
            """, unsafe_allow_html=True)

            # 舱位对比
            st.markdown("<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;'>",
                       unsafe_allow_html=True)
            st.markdown("<span style='color: #6b7280; font-weight: 500;'>各舱位价格对比</span>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)

            cols = st.columns(3)
            for idx, (cabin_type, cabin_data) in enumerate(cabin_prices.items()):
                with cols[idx]:
                    is_selected = cabin_type == selected_cabin
                    border_color = "#10b981" if is_selected else "#e5e7eb"
                    bg_color = "#f0fdf4" if is_selected else "#ffffff"

                    # ✅ 检查该舱位是否可负担
                    cabin_can_afford = cabin_data['price'] <= remaining_budget

                    st.markdown(f"""
                    <div style='padding: 12px; border: 2px solid {border_color}; 
                                border-radius: 8px; text-align: center; background: {bg_color};'>
                        <div style='font-size: 13px; color: #6b7280; margin-bottom: 4px;'>
                            {cabin_data['name']}
                        </div>
                        <div style='font-size: 18px; font-weight: 700; color: {"#10b981" if cabin_can_afford else "#ef4444"};'>
                            ¥{cabin_data['price']:,}
                        </div>
                        <div style='font-size: 11px; color: {"#065f46" if cabin_can_afford else "#991b1b"};'>
                            {"✅ 可负担" if cabin_can_afford else "❌ 预算不足"}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

            # 服务说明
            st.markdown("<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;'>",
                       unsafe_allow_html=True)
            st.markdown("<span style='color: #6b7280; font-weight: 500;'>服务说明</span>", unsafe_allow_html=True)

            service_items = [
                "✓ 免费WiFi(部分航班)",
                "✓ 机上娱乐系统",
                "✓ 餐食饮料服务",
                "✓ 免费改期(限当日)"
            ]

            for item in service_items:
                st.markdown(f"<div style='color: #374151; font-size: 13px; padding: 2px 0;'>{item}</div>",
                           unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return None


def display_flight_list_v2(flights, message_id=0, on_book_callback=None):
    """
    航班列表展示 - 带统一预算管理

    参数:
        flights: 航班列表
        message_id: 消息ID
        on_book_callback: 预订回调函数
    """
    if not flights:
        st.info("未找到符合条件的航班")
        return

    # ✅ 显示剩余预算
    remaining_budget = get_remaining_budget()

    col_result, col_budget = st.columns([2, 1])
    with col_result:
        st.markdown(f"""
        <div style='background: #d1fae5; border: 1px solid #10b981; border-radius: 8px; 
                    padding: 12px 16px; margin-bottom: 16px;'>
            <span style='color: #047857; font-size: 14px;'>
                找到 <strong>{len(flights)}</strong> 个航班
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_budget:
        st.metric("💰 剩余预算", f"¥{remaining_budget:,}")

    # 筛选器
    with st.expander("筛选条件", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            max_price = st.number_input(
                "最高价格(元)",
                min_value=0,
                max_value=10000,
                value=min(5000, int(remaining_budget)) if remaining_budget > 0 else 5000,
                step=100,
                key=f"flight_price_{message_id}"
            )

        with col2:
            flight_time = st.selectbox(
                "时间段",
                options=["全部", "上午(06:00-12:00)", "下午(12:00-18:00)", "晚上(18:00-24:00)"],
                key=f"flight_time_{message_id}"
            )

        with col3:
            stops_filter = st.selectbox(
                "经停",
                options=["全部", "仅直飞", "1次经停"],
                key=f"flight_stops_{message_id}"
            )

    # 筛选航班
    filtered = []
    for flight in flights:
        if flight.get('price', 0) > max_price:
            continue

        if flight_time != "全部":
            dep_time = flight.get('departure_time', '00:00')
            hour = int(dep_time.split(':')[0])

            if flight_time == "上午(06:00-12:00)" and not (6 <= hour < 12):
                continue
            elif flight_time == "下午(12:00-18:00)" and not (12 <= hour < 18):
                continue
            elif flight_time == "晚上(18:00-24:00)" and not (18 <= hour < 24):
                continue

        stops = flight.get('stops', 0)
        if stops_filter == "仅直飞" and stops != 0:
            continue
        elif stops_filter == "1次经停" and stops != 1:
            continue

        filtered.append(flight)

    if not filtered:
        st.warning("没有符合筛选条件的航班")
        return

    # 排序选项
    col_sort1, col_sort2 = st.columns([3, 1])
    with col_sort2:
        sort_by = st.selectbox(
            "排序",
            options=["价格从低到高", "价格从高到低", "起飞时间"],
            key=f"flight_sort_{message_id}",
            label_visibility="collapsed"
        )

    if sort_by == "价格从低到高":
        filtered.sort(key=lambda x: x.get('price', 0))
    elif sort_by == "价格从高到低":
        filtered.sort(key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == "起飞时间":
        filtered.sort(key=lambda x: x.get('departure_time', '00:00'))

    # 显示航班卡片
    for flight in filtered[:10]:
        display_flight_card_v2(
            flight,
            key_prefix="flight",
            message_id=message_id,
            on_book_callback=on_book_callback
        )


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="仿真机票卡片 - 统一预算版", layout="wide")

    st.title("仿真机票卡片组件 - 统一预算版")
    st.caption("演示统一预算管理和舱位选择")

    # 模拟预算状态
    if "total_spent" not in st.session_state:
        st.session_state.total_spent = 0

    if "current_trip" not in st.session_state:
        st.session_state.current_trip = {"budget": 5000}

    # 侧边栏显示预算
    with st.sidebar:
        st.header("💰 预算管理")
        total_budget = st.session_state.current_trip["budget"]
        remaining = total_budget - st.session_state.total_spent

        st.metric("总预算", f"¥{total_budget:,}")
        st.metric("剩余", f"¥{remaining:,}", delta=f"-¥{st.session_state.total_spent:,}")
        st.progress(min(st.session_state.total_spent / total_budget, 1.0))

    test_flights = [
        {
            'id': 1,
            'carrier_code': 'CA',
            'carrier_name': '中国国航',
            'flight_number': '1234',
            'origin': '北京',
            'destination': '上海',
            'departure_time': '08:30',
            'arrival_time': '11:00',
            'departure_date': '2025-01-15',
            'duration': '2小时30分钟',
            'price': 850,
            'aircraft': '波音737',
            'stops': 0,
            'available_seats': 25
        },
        {
            'id': 2,
            'carrier_code': 'MU',
            'carrier_name': '东方航空',
            'flight_number': '5678',
            'origin': '北京',
            'destination': '上海',
            'departure_time': '14:15',
            'arrival_time': '16:50',
            'departure_date': '2025-01-15',
            'duration': '2小时35分钟',
            'price': 720,
            'aircraft': '空客A320',
            'stops': 0,
            'available_seats': 18
        }
    ]

    def test_booking_callback(order_type, flight, price):
        """测试预订回调"""
        st.session_state.total_spent += price
        st.success(f"""
        ✅ 预订成功!
        
        - 航班: {flight['carrier_name']} {flight['flight_number']}
        - 舱位: {flight.get('cabin_class', 'N/A')}
        - 价格: ¥{price:,}
        - 剩余预算: ¥{get_remaining_budget():,}
        """)
        st.balloons()

    display_flight_list_v2(test_flights, message_id=0, on_book_callback=test_booking_callback)