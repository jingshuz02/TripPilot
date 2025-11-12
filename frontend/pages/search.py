import streamlit as st
from datetime import datetime, timedelta
from uuid import uuid4

# 支付处理函数
def process_payment():
    if st.session_state.current_payment is None:
        return

    trip_id, item_name, price, item_id = st.session_state.current_payment
    password = st.text_input("Payment Password (Test: 1234)", type="password")
    
    total_spent = sum(o['price'] for o in st.session_state.orders if o.get('trip_id') == trip_id)
    remaining = st.session_state.budget - total_spent

    if st.button("Confirm Payment", type="primary", key=f"confirm_pay_{item_id}"):
        if password == "1234" and price <= remaining:
            order_id = str(uuid4())[:8]
            st.session_state.orders.append({
                "id": order_id,
                "item": item_name,
                "price": price,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "trip_id": trip_id,
                "status": "Paid"
            })
            st.session_state.current_payment = None
            st.success(f"✅ Payment Successful! Order No.: {order_id}")
            st.rerun()
        else:
            st.error("❌ Invalid password or insufficient budget")

# 页面标题
st.title("🔍 Search & Book Services")

# 酒店搜索表单
with st.container(border=True):
    st.subheader("🏨 Hotel Search")
    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.text_input("City", "Tokyo")
    with col2:
        check_in = st.date_input("Check-in Date", datetime.now())
    with col3:
        check_out = st.date_input("Check-out Date", datetime.now() + timedelta(days=2))
    
    if st.button("Search Hotels", type="primary"):
        with st.spinner("Searching hotels..."):
            # 调用酒店搜索接口（离线时使用预设数据）
            result = st.session_state.api_client.search_hotels(
                city=city,
                check_in=check_in.strftime("%Y-%m-%d"),
                check_out=check_out.strftime("%Y-%m-%d")
            )
            if not result:
                st.info("Using preset hotels (backend not connected)")

# 显示酒店列表（优先显示搜索结果，无结果则显示预设酒店）
st.subheader("Available Hotels")
hotels_to_show = st.session_state.preset_hotels  # 默认使用预设酒店

for idx, hotel in enumerate(hotels_to_show):
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"### {hotel['name']}")
            st.write(hotel["desc"])
        with col2:
            st.write(f"**Price: ${hotel['price']}**")
            default_trip_id = st.session_state.trips[0]["id"]
            item_id = f"hotel_{idx}"
            if st.button("Book", key=f"book_hotel_{idx}"):
                st.session_state.current_payment = (default_trip_id, hotel["name"], hotel["price"], item_id)
                st.rerun()

# 支付区域（有支付项时显示）
if st.session_state.current_payment is not None:
    trip_id, item_name, price, item_id = st.session_state.current_payment
    total_spent = sum(o['price'] for o in st.session_state.orders if o.get('trip_id') == trip_id)
    remaining = st.session_state.budget - total_spent

    with st.container(border=True, key="payment_container"):
        st.subheader(f"📌 Confirm Booking - {item_name}")
        st.write(f"**Price**: ${price}")
        st.write(f"**Remaining Budget**: ${remaining}")
        st.text_input("Card Number (Test: 1234 5678 9012 3456)", "1234 5678 9012 3456", disabled=True)
        process_payment()

# 侧边栏：快速预订服务
with st.sidebar:
    st.header("💳 Quick Booking")
    for trip in st.session_state.trips:
        with st.expander(trip["name"], expanded=True):
            service_name = st.text_input(
                f"Service Name for {trip['name']}", 
                placeholder="e.g., Tokyo Hotel"
            )
            service_price = st.number_input(
                f"Price (USD)", 
                min_value=0, 
                step=10
            )
            
            item_id = f"{trip['id']}_{service_name}" if service_name else ""
            if st.button(
                "Book Now", 
                type="primary", 
                disabled=not (service_name and service_price > 0),
                key=f"service_book_{item_id}"
            ):
                st.session_state.current_payment = (trip['id'], service_name, service_price, item_id)
                st.rerun()
