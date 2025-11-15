import streamlit as st
from datetime import datetime

def display_flight_card(flight_data, key_prefix="flight"):
    """
    显示航班卡片（蓝色主题）
    
    参数:
        flight_data (dict): 航班数据（对应数据库字段）
        key_prefix (str): 按钮key前缀
    
    返回:
        str: 用户操作 ("book", "details" 或 None)
    """
    
    # 清新蓝色主题 CSS
    st.markdown("""
    <style>
    .flight-card {
        border: 1px solid #bee3f8;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        background: linear-gradient(to right, #e6fffa 0%, #ffffff 100%);
        transition: all 0.3s;
    }
    .flight-card:hover {
        box-shadow: 0 6px 12px rgba(72, 187, 120, 0.15);
        transform: translateY(-2px);
    }
    .flight-route {
        font-size: 22px;
        font-weight: bold;
        color: #2c5282;
        margin-bottom: 10px;
    }
    .flight-time {
        font-size: 18px;
        color: #2d3748;
        font-weight: 600;
    }
    .flight-duration {
        color: #718096;
        font-size: 14px;
        text-align: center;
    }
    .flight-info {
        color: #4a5568;
        font-size: 13px;
        margin-top: 8px;
    }
    .flight-price {
        font-size: 28px;
        font-weight: bold;
        color: #38a169;
    }
    .flight-cabin {
        background: #c6f6d5;
        color: #276749;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown("<div class='flight-card'>", unsafe_allow_html=True)
        
        # 航班路线
        departure_iata = flight_data.get('departure_iata', 'XXX')
        arrival_iata = flight_data.get('arrival_iata', 'XXX')
        st.markdown(f"<div class='flight-route'>✈️ {departure_iata} → {arrival_iata}</div>", unsafe_allow_html=True)
        
        # 时间信息
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            departure_time = flight_data.get('departure_time', 'N/A')
            try:
                dep_dt = datetime.fromisoformat(departure_time.replace('Z', '+00:00'))
                dep_display = dep_dt.strftime("%H:%M")
            except:
                dep_display = departure_time
            st.markdown(f"<div class='flight-time'>🛫 {dep_display}</div>", unsafe_allow_html=True)
            st.caption(f"出发 · {departure_iata}")
        
        with col2:
            duration = flight_data.get('duration', 'N/A')
            st.markdown(f"<div class='flight-duration'>⏱️ {duration}</div>", unsafe_allow_html=True)
            st.markdown("<div style='text-align: center; color: #cbd5e0;'>━━━━━</div>", unsafe_allow_html=True)
        
        with col3:
            arrival_time = flight_data.get('arrival_time', 'N/A')
            try:
                arr_dt = datetime.fromisoformat(arrival_time.replace('Z', '+00:00'))
                arr_display = arr_dt.strftime("%H:%M")
            except:
                arr_display = arrival_time
            st.markdown(f"<div class='flight-time'>🛬 {arr_display}</div>", unsafe_allow_html=True)
            st.caption(f"到达 · {arrival_iata}")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 航班详情
        col_a, col_b, col_c = st.columns(3)
        
        with col_a:
            carrier = flight_data.get('carrier_code', 'XX')
            flight_num = flight_data.get('flight_number', '000')
            st.markdown(f"<div class='flight-info'>🏷️ {carrier} {flight_num}</div>", unsafe_allow_html=True)
            
            aircraft = flight_data.get('aircraft_code', 'N/A')
            st.markdown(f"<div class='flight-info'>🛩️ {aircraft}</div>", unsafe_allow_html=True)
        
        with col_b:
            cabin_class = flight_data.get('cabin_class', 'ECONOMY')
            cabin_display = {
                'ECONOMY': '经济舱',
                'PREMIUM_ECONOMY': '超经舱',
                'BUSINESS': '商务舱',
                'FIRST': '头等舱'
            }.get(cabin_class, cabin_class)
            
            st.markdown(f"<span class='flight-cabin'>{cabin_display}</span>", unsafe_allow_html=True)
            
            # 预留amenities详情按钮空间
            st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
        
        with col_c:
            # 价格和货币
            price = flight_data.get('total_price', 0)
            currency = flight_data.get('currency', 'USD')
            st.markdown(f"<div class='flight-price'>{currency} {price:.2f}</div>", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # 操作按钮
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        
        action = None
        
        with col_btn1:
            if st.button("📋 查看详情", key=f"{key_prefix}_details", use_container_width=True):
                action = "details"
        
        with col_btn2:
            # 预留amenities按钮空间
            seats = flight_data.get('number_of_bookable_seats', 0)
            if seats > 0:
                st.caption(f"剩余 {seats} 座")
        
        with col_btn3:
            if st.button("💳 预订", key=f"{key_prefix}_book", type="primary", use_container_width=True):
                action = "book"
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    return action


def display_flight_details_modal(flight_data, amenities_data=None):
    """
    显示航班详细信息模态框（包含amenities）
    
    参数:
        flight_data (dict): 航班数据
        amenities_data (list): 便利设施列表 [{service: str, is_chargeable: bool}, ...]
    """
    
    st.subheader("✈️ 航班详细信息")
    
    with st.container(border=True):
        # 基本信息
        st.markdown("#### 📌 基本信息")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**航班号**: {flight_data.get('carrier_code', 'XX')} {flight_data.get('flight_number', '000')}")
            st.write(f"**机型**: {flight_data.get('aircraft_code', 'N/A')}")
            st.write(f"**舱位**: {flight_data.get('cabin_class', 'N/A')}")
        
        with col2:
            st.write(f"**运营商**: {flight_data.get('operating_carrier', 'N/A')}")
            st.write(f"**可订座位**: {flight_data.get('number_of_bookable_seats', 0)}")
            st.write(f"**出票截止**: {flight_data.get('last_ticketing_date', 'N/A')}")
        
        st.divider()
        
        # 行李信息
        st.markdown("#### 🧳 行李额度")
        col_a, col_b = st.columns(2)
        
        with col_a:
            checked_bags = flight_data.get('included_checked_bags', 'N/A')
            st.write(f"**托运行李**: {checked_bags}")
        
        with col_b:
            cabin_bags = flight_data.get('included_cabin_bags', 'N/A')
            st.write(f"**手提行李**: {cabin_bags}")
        
        st.divider()
        
        # 便利设施（amenities）
        st.markdown("#### 🎁 附加服务")
        
        if amenities_data and len(amenities_data) > 0:
            # 显示amenities表格
            st.markdown("""
            <style>
            .amenity-table {
                width: 100%;
                border-collapse: collapse;
            }
            .amenity-table th {
                background: #ebf8ff;
                color: #2c5282;
                padding: 10px;
                text-align: left;
                font-weight: 600;
            }
            .amenity-table td {
                padding: 10px;
                border-bottom: 1px solid #e2e8f0;
            }
            .amenity-free {
                color: #38a169;
                font-weight: 600;
            }
            .amenity-paid {
                color: #dd6b20;
                font-weight: 600;
            }
            </style>
            """, unsafe_allow_html=True)
            
            table_html = "<table class='amenity-table'><thead><tr><th>服务项目</th><th>费用</th></tr></thead><tbody>"
            
            for amenity in amenities_data:
                service = amenity.get('service', 'N/A')
                is_chargeable = amenity.get('is_chargeable', False)
                
                fee_class = "amenity-paid" if is_chargeable else "amenity-free"
                fee_text = "收费" if is_chargeable else "免费"
                
                table_html += f"<tr><td>{service}</td><td class='{fee_class}'>{fee_text}</td></tr>"
            
            table_html += "</tbody></table>"
            st.markdown(table_html, unsafe_allow_html=True)
        else:
            st.info("暂无附加服务信息")
        
        st.divider()
        
        # 价格明细
        st.markdown("#### 💰 价格明细")
        col_x, col_y = st.columns(2)
        
        with col_x:
            st.write(f"**基础票价**: {flight_data.get('currency', 'USD')} {flight_data.get('base_price', 0):.2f}")
        
        with col_y:
            st.write(f"**总价**: {flight_data.get('currency', 'USD')} {flight_data.get('grand_total', 0):.2f}")