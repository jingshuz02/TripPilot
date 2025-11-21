"""
TripPilot - Intelligent Travel Assistant
Main Entry File
"""
import streamlit as st
import sys
import os
from datetime import datetime
from uuid import uuid4

# ==================== 1. Resolve Icon Path Issue (Verify Path in Advance) ====================
# Define and verify the icon path to avoid errors
icon_path = os.path.join("frontend", "images", "logo.jpg")


# ==================== 2. Page Configuration (Use Verified Icon Path) ====================
st.set_page_config(
    page_title="TripPilot - Intelligent Travel Assistant",
    page_icon=icon_path if os.path.exists(icon_path) else "✈️",  # Use custom icon if path is correct, default airplane otherwise
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 3. Global Styles ====================
st.markdown("""
<style>
    /* Theme Color */
    .stApp {
        background-color: #f8f9fa;
    }
    /* Chat Message Style */
    .stChatMessage {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }
    /* Container Border */
    .element-container {
        border-radius: 8px;
    }
    /* Button Style */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Metric Card */
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Hide Duplicate Deprecation Warnings (Key! Resolve Duplicate Text Issue) */
    .stAlert:has(.deprecation-warning) {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 4. Global State Initialization ====================
def init_session_state():
    """Initialize all session states"""
    # Trip List
    if "trips" not in st.session_state:
        st.session_state.trips = [{
            "name": "My Travel Plan",
            "desc": "Automatically created default trip",
            "id": str(uuid4())[:8],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "destination": "",
            "start_date": "",
            "end_date": ""
        }]
    # Order List
    if "orders" not in st.session_state:
        st.session_state.orders = []
    # Budget
    if "budget" not in st.session_state:
        st.session_state.budget = 5000
    # Current Payment Info
    if "current_payment" not in st.session_state:
        st.session_state.current_payment = None
    # Message History
    if "messages" not in st.session_state:
        st.session_state.messages = []
    # Destination
    if "destination" not in st.session_state:
        st.session_state.destination = ""
    # Travel Dates
    if "start_date" not in st.session_state:
        st.session_state.start_date = ""
    if "end_date" not in st.session_state:
        st.session_state.end_date = ""
    # Preset Hotel Data (for demo)
    if "preset_hotels" not in st.session_state:
        st.session_state.preset_hotels = [
            {
                "name": "Tokyo Sensoji Hotel (3 Nights)",
                "price": 450,
                "desc": "5-minute walk to attractions, breakfast included",
                "location": "Tokyo",
                "rating": 4.5
            },
            {
                "name": "Shibuya Modern Hotel (2 Nights)",
                "price": 380,
                "desc": "Near shopping area, free WiFi",
                "location": "Tokyo",
                "rating": 4.2
            },
            {
                "name": "Tokyo Bay Resort (4 Nights)",
                "price": 620,
                "desc": "Ocean view room, 3 meals included",
                "location": "Tokyo",
                "rating": 4.8
            }
        ]
init_session_state()

# ==================== 5. Main Page Content (Place Icon First, Then Title, Avoid Overlapping) ====================
# Top-left icon layout (Place at the very front to ensure it's not pushed by other content)
col_icon, col_title = st.columns([1, 8])  # Icon takes 1 part, title takes 8 parts, ensure icon is left-aligned
with col_icon:
    if os.path.exists(icon_path):
        st.image(
            icon_path,
            width=160,  # Icon size, adapted to top-left
            use_container_width=False,
            output_format="JPG"
        )
with col_title:
    st.title("TripPilot - Intelligent Travel Assistant")
st.caption("Powered by AI | Make Travel Planning Easier")

# Welcome Message
st.markdown("""
### Welcome to TripPilot!

I'm your dedicated AI travel advisor, here to help you:
-  **Search Flights & Hotels** - Quickly find the best options
-  **Check Weather** - Stay updated on destination weather  
-  **Plan Itineraries** - Get smart travel route recommendations
-  **Manage Budget** - Track travel expenses in real-time
""")

st.divider()

# Quick Stats
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Budget",
        f"${st.session_state.budget}",
        delta=None
    )

with col2:
    total_spent = sum(o['price'] for o in st.session_state.orders)
    st.metric(
        "Total Spent",
        f"${total_spent:.2f}",
        delta=f"-{total_spent / st.session_state.budget * 100:.1f}%" if st.session_state.budget > 0 else None
    )

with col3:
    st.metric(
        "Number of Orders",
        len(st.session_state.orders),
        delta=None
    )

with col4:
    st.metric(
        "Number of Trips",
        len(st.session_state.trips),
        delta=None
    )

st.divider()

# Quick Start
st.markdown("### Quick Start")

col_a, col_b = st.columns(2)

with col_a:
    if st.button("💬 Start Chat", use_container_width=True, type="primary"):
        st.switch_page("pages/chat.py")

    st.caption("Chat with AI assistant to plan your trip")

with col_b:
    if st.button("View Orders", use_container_width=True):
        st.switch_page("pages/order.py")

    st.caption("Manage your flight and hotel bookings")

st.divider()

# User Guide
with st.expander(" User Guide", expanded=False):
    st.markdown("""
    #### How to Use TripPilot?

    1. **Start Chatting**
       - Click "Start Chat" to enter the chat page
       - Tell me your travel needs, e.g.: "Find flights from Hong Kong to Tokyo"

    2. **View Recommendations**
       - AI will search and display flight/hotel options
       - Use filters to find the perfect match

    3. **Book**
       - Click "Book" to add items to your orders
       - System automatically tracks budget usage

    4. **Manage Orders**
       - View all bookings on the "Orders" page
       - Confirm, delete, or export orders as needed

    #### Tips
    - Adjust your budget anytime in the sidebar
    - Support parallel management of multiple trips
    - All data is saved in the current session
    """)

# ==================== Sidebar ====================

with st.sidebar:
    st.header("System Settings")

    # Backend Status Check
    st.markdown("####Backend Connection")

    import requests

    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            st.success("Backend Service Normal")
        else:
            st.error("Backend Service Abnormal")
    except:
        st.error("Backend Service Not Started")
        st.caption("Please run: `python app.py`")

    st.divider()

    # Quick Settings
    st.markdown("#### Quick Settings")

    # Destination
    destination = st.text_input(
        "Destination",
        value=st.session_state.destination,
        placeholder="e.g.: Tokyo"
    )
    if destination != st.session_state.destination:
        st.session_state.destination = destination

    # Travel Dates
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date()
        )
    with col_date2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date()
        )

    st.session_state.start_date = str(start_date)
    st.session_state.end_date = str(end_date)

    st.divider()

    # About
    st.markdown("#### About")
    st.caption("""
    **TripPilot v1.0**  
    Intelligent Travel Planning Assistant  

    Powered by AI, providing flight, hotel, weather search and itinerary planning services.
    """)

    # Feedback
    if st.button("💬 Provide Feedback", use_container_width=True):
        st.info("Thank you for your feedback! Feature in development...")

# ==================== Footer ====================

st.markdown("---")
st.caption("TripPilot © 2025 | Powered by Deepseek")
