

import streamlit as st
import requests
import os
import sys
from datetime import datetime
from uuid import uuid4
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(
    page_title="TripPilot - Your Travel Assistant",
    page_icon="✈️",
    layout="wide"
)


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "api_connected" not in st.session_state:
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            st.session_state.api_connected = response.status_code == 200
        except:
            st.session_state.api_connected = False
    if "trips" not in st.session_state:
        st.session_state.trips = []
    if "orders" not in st.session_state:
        st.session_state.orders = []
    if "budget" not in st.session_state:
        st.session_state.budget = 1000
    if "current_payment" not in st.session_state:
        st.session_state.current_payment = None  # (trip_id, item_name, price, item_id)
    if "preset_hotels" not in st.session_state:
        st.session_state.preset_hotels = [
            {"name": "Asakusa Temple Hotel (3 Nights)", "price": 450, "desc": "5-minute walk to attractions, breakfast included"},
            {"name": "Shibuya Modern Hotel (2 Nights)", "price": 380, "desc": "Near shopping district, free wifi"},
            {"name": "Tokyo Bay Resort (4 Nights)", "price": 620, "desc": "Ocean view, all-inclusive meals"}
        ]
    if not st.session_state.trips:
        st.session_state.trips.append({
            "name": "Default Trip Plan",
            "desc": "Auto-created on page load",
            "id": str(uuid4())[:8],
            "created_at": datetime.now().strftime("%Y-%m-%d")
        })


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


init_session_state()

# 主标题和预算状态
col1, col2 = st.columns([3, 1])
with col1:
    st.title("✈️ TripPilot - Intelligent Travel Planning Assistant")
    st.caption("Powered by DeepSeek AI")
with col2:
    total_spent = sum(o['price'] for o in st.session_state.orders)
    remaining = st.session_state.budget - total_spent
    st.metric("Budget Status", f"${remaining}", f"Total: ${st.session_state.budget}")


# 侧边栏：旅行计划和订单模块
with st.sidebar:
    st.header("📅 My Trip Plans")
    for trip in st.session_state.trips:
        with st.expander(trip["name"], expanded=True):
            st.write(trip["desc"])
            st.caption(f"Created at: {trip['created_at']} | ID: {trip['id']}")

            st.subheader("📋 My Orders")
            trip_orders = [o for o in st.session_state.orders if o.get('trip_id') == trip['id']]
            if trip_orders:
                for o in trip_orders:
                    st.write(f"• {o['item']} - ${o['price']} ({o['time']}) | {o['status']}")
                st.write(f"**Total Spent**: ${sum(o['price'] for o in trip_orders)}")
            else:
                st.markdown("""
                    <div style="background-color: #e6f2ff; padding: 10px; border-radius: 5px;">
                        No orders yet
                    </div>
                    """, unsafe_allow_html=True)

            if st.button("Clear Order History", key=f"clear_order_{trip['id']}"):
                st.session_state.orders = [o for o in st.session_state.orders if o.get('trip_id') != trip['id']]
                st.rerun()

            st.divider()

            st.subheader("💳 Book Services")
            service_name = st.text_input(f"Service Name", placeholder="e.g., Tokyo Hotel")
            service_price = st.number_input(f"Price (USD)", min_value=0, step=10)
            
            item_id = f"{trip['id']}_{service_name}" if service_name else ""
            if st.button("Book Now", type="primary", 
                       disabled=not (service_name and service_price > 0),
                       key=f"service_book_{item_id}"):
                st.session_state.current_payment = (trip['id'], service_name, service_price, item_id)
                st.rerun()

    st.divider()
    st.header("⚙️ Settings")
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.api_connected:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Disconnected")
    with col2:
        if st.button("🔄"):
            try:
                response = requests.get("http://localhost:5000/health", timeout=2)
                st.session_state.api_connected = response.status_code == 200
            except:
                st.session_state.api_connected = False
            st.rerun()

    if not st.session_state.api_connected:
        st.info("📝 Start backend:\n```\npython backend/app.py\n```")

    st.divider()
    st.subheader("🎯 Travel Preferences")
    st.session_state.budget = st.number_input("Budget (USD)", min_value=0, value=1000, step=100)
    start_date = st.date_input("Departure Date", value=datetime.now())
    end_date = st.date_input("Return Date")
    language = st.selectbox("Language", ["English", "中文", "日本語"])

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()


# 主界面：酒店列表和右侧支付区域
st.subheader("🏨 Hotel Listings")
for idx, hotel in enumerate(st.session_state.preset_hotels):
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

# 右侧支付区域（仅在有支付项时显示）
if st.session_state.current_payment is not None:
    trip_id, item_name, price, item_id = st.session_state.current_payment
    total_spent = sum(o['price'] for o in st.session_state.orders if o.get('trip_id') == trip_id)
    remaining = st.session_state.budget - total_spent

    with st.container(border=True, key="payment_container"):
        st.subheader(f"Confirm Booking - {item_name}")
        st.write(f"**Price**: ${price}")
        st.write(f"**Remaining Budget**: ${remaining}")
        st.text_input("Card Number (Test: 1234 5678 9012 3456)", "1234 5678 9012 3456", disabled=True)
        process_payment()


# 聊天界面
st.subheader("💬 Chat with TripPilot")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask for trip plans..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            if st.session_state.api_connected:
                try:
                    trip_name = f"AI-Generated Trip - {prompt[:20]}"
                    trip_desc = "Generated by AI: " + prompt
                    st.session_state.trips.append({
                        "name": trip_name, "desc": trip_desc,
                        "id": str(uuid4())[:8], "created_at": datetime.now().strftime("%Y-%m-%d")
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Generation failed: {str(e)}")
            else:
                st.write("Backend not connected. Use preset hotels below.")
