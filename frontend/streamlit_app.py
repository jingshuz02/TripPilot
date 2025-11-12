import streamlit as st
import sys
import os

# Initialize global state 
def init_global_state():
    if "api_client" not in st.session_state:
        from api_client import APIClient  
        st.session_state.api_client = APIClient()  
    if "trips" not in st.session_state:
        from uuid import uuid4
        from datetime import datetime
        st.session_state.trips = [{
            "name": "Default Trip Plan",
            "desc": "Auto-created on page load",
            "id": str(uuid4())[:8],
            "created_at": datetime.now().strftime("%Y-%m-%d")
        }]
    if "orders" not in st.session_state:
        st.session_state.orders = []
    if "budget" not in st.session_state:
        st.session_state.budget = 1000
    if "current_payment" not in st.session_state:
        st.session_state.current_payment = None  
    if "preset_hotels" not in st.session_state:
        st.session_state.preset_hotels = [
            {"name": "Asakusa Temple Hotel (3 Nights)", "price": 450, "desc": "5-minute walk to attractions, breakfast included"},
            {"name": "Shibuya Modern Hotel (2 Nights)", "price": 380, "desc": "Near shopping district, free wifi"},
            {"name": "Tokyo Bay Resort (4 Nights)", "price": 620, "desc": "Ocean view, all-inclusive meals"}
        ]

# Configure page
st.set_page_config(
    page_title="TripPilot - Your Travel Assistant",
    page_icon="✈️",
    layout="wide"
)

# Initialize global state
init_global_state()

# Compatibility with older versions: directly redirect to chat page (remove get_page_config check)
st.switch_page("pages/chat.py")  # Execute redirect directly without checks


# Main page content (won't be displayed after redirect, can be kept)
st.title("✈️ TripPilot - Intelligent Travel Planning Assistant")
st.caption("Powered by DeepSeek AI")

total_spent = sum(o['price'] for o in st.session_state.orders)
remaining = st.session_state.budget - total_spent
delta_color = "inverse" if remaining < 0 else "normal"
st.metric(
    "Budget Status", 
    f"${remaining}", 
    f"Total: ${st.session_state.budget}", 
    delta_color=delta_color
)

st.divider()
st.info("Select a feature from the left navigation")
