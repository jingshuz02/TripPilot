"""
TripPilot - Intelligent Travel Assistant
Main Entry File - Enhanced with Conversation Management
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
    page_icon=icon_path if os.path.exists(icon_path) else "✈️",
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
    /* Hide Duplicate Deprecation Warnings */
    .stAlert:has(.deprecation-warning) {
        display: none !important;
    }
    
    /* Conversation Item Style */
    .conversation-item {
        padding: 10px;
        margin: 5px 0;
        border-radius: 8px;
        background-color: white;
        cursor: pointer;
        transition: all 0.2s;
    }
    
    .conversation-item:hover {
        background-color: #f0f0f0;
        transform: translateX(5px);
    }
    
    .conversation-item.active {
        background-color: #10b981;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 4. Global State Initialization ====================
def init_session_state():
    """Initialize all session states"""

    # ========== Conversation Management (统一数据结构) ==========
    if "conversations" not in st.session_state:
        default_conv_id = str(uuid4())[:8]
        st.session_state.conversations = {
            default_conv_id: {
                "id": default_conv_id,
                "name": "New Conversation",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "messages": [],
                # ✅ 统一使用 preferences 结构
                "preferences": {
                    "destination": "",
                    "days": 3,
                    "budget": 5000,
                    "start_date": datetime.now().date(),
                    "end_date": None
                }
            }
        }
        st.session_state.current_conversation_id = default_conv_id

    # ✅ 修复旧对话数据结构（向后兼容）
    for conv_id, conv in st.session_state.conversations.items():
        if "preferences" not in conv:
            conv["preferences"] = {
                "destination": conv.get("destination", ""),
                "days": 3,
                "budget": 5000,
                "start_date": datetime.now().date(),
                "end_date": None
            }
        # 清理旧字段
        conv.pop("destination", None)
        conv.pop("start_date", None)
        conv.pop("end_date", None)

    # Ensure current conversation ID is valid
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
    elif st.session_state.current_conversation_id not in st.session_state.conversations:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]

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

    # Message History (for backward compatibility)
    if "messages" not in st.session_state:
        current_conv = get_current_conversation()
        st.session_state.messages = current_conv["messages"] if current_conv else []

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


# ==================== Conversation Management Functions ====================

def create_new_conversation():
    """Create a new conversation"""
    new_conv_id = str(uuid4())[:8]
    st.session_state.conversations[new_conv_id] = {
        "id": new_conv_id,
        "name": f"New Conversation {len(st.session_state.conversations) + 1}",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "messages": [],
        "preferences": {
            "destination": "",
            "days": 3,
            "budget": 5000,
            "start_date": datetime.now().date(),
            "end_date": None
        }
    }
    st.session_state.current_conversation_id = new_conv_id
    st.success("✅ New conversation created")


def switch_conversation(conv_id: str):
    """Switch conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id


def delete_conversation(conv_id: str):
    """Delete conversation"""
    if len(st.session_state.conversations) <= 1:
        st.error("❌ Must keep at least one conversation")
        return

    if conv_id in st.session_state.conversations:
        del st.session_state.conversations[conv_id]

        # Switch to the first conversation
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
        st.success("✅ Conversation deleted")


def rename_conversation(conv_id: str, new_name: str):
    """Rename conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["name"] = new_name
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        st.success("✅ Conversation renamed")


def get_current_conversation():
    """Get current conversation"""
    conv_id = st.session_state.current_conversation_id
    return st.session_state.conversations.get(conv_id)


# Initialize
init_session_state()

# ==================== 5. Main Page Content ====================
# Top-left icon layout
col_icon, col_title = st.columns([1, 8])
with col_icon:
    if os.path.exists(icon_path):
        st.image(
            icon_path,
            width=160,
            use_container_width=False,
            output_format="JPG"
        )
with col_title:
    st.title("TripPilot - Intelligent Travel Assistant")
st.caption("Powered by AI | Make Travel Planning Easier")

# Welcome Message
st.markdown("""
### 👋 Welcome to TripPilot!

I'm your dedicated AI travel advisor, here to help you:
- 🔍 **Search Flights & Hotels** - Quickly find the best options
- 🌤️ **Check Weather** - Stay updated on destination weather  
- 📋 **Plan Itineraries** - Get smart travel route recommendations
- 💰 **Manage Budget** - Track travel expenses in real-time
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
        "Conversations",
        len(st.session_state.conversations),
        delta=None
    )

st.divider()

# Quick Start
st.markdown("### 🚀 Quick Start")

col_a, col_b = st.columns(2)

with col_a:
    if st.button("💬 Start Chat", use_container_width=True, type="primary"):
        st.switch_page("pages/chat.py")

    st.caption("Chat with AI assistant to plan your trip")

with col_b:
    if st.button("📋 View Orders", use_container_width=True):
        st.switch_page("pages/order.py")

    st.caption("Manage your flight and hotel bookings")

st.divider()

# User Guide
with st.expander("📖 User Guide", expanded=False):
    st.markdown("""
    #### How to Use TripPilot?

    1. **Start Chatting**
       - Click "Start Chat" to enter the chat page
       - Tell me your travel needs, e.g.: "Find flights from Hong Kong to Tokyo"

    2. **Manage Conversations** (New!)
       - Create multiple conversations for different trips
       - Each conversation saves independently
       - Switch, rename, or delete conversations anytime
       - All conversations are auto-saved

    3. **View Recommendations**
       - AI will search and display flight/hotel options
       - Use filters to find the perfect match

    4. **Book**
       - Click "Book" to add items to your orders
       - System automatically tracks budget usage

    5. **Manage Orders**
       - View all bookings on the "Orders" page
       - Confirm, delete, or export orders as needed

    #### 💡 Tips
    - Adjust your budget anytime in the sidebar
    - Support parallel management of multiple conversations
    - All data is saved in the current session
    - Refresh won't lose your conversations
    """)

# ==================== Sidebar ====================

with st.sidebar:
    st.header("⚙️ System Settings")

    # Backend Status Check
    st.markdown("#### 📌 Backend Connection")

    import requests

    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Service Normal")
        else:
            st.error("❌ Backend Service Abnormal")
    except:
        st.error("❌ Backend Service Not Started")
        st.caption("Please run: `python app.py`")

    st.divider()

    # ========== Conversation Management ==========
    st.markdown("#### 💬 Conversation Management")

    # New conversation button
    if st.button("➕ New Conversation", use_container_width=True, type="primary"):
        create_new_conversation()
        st.rerun()

    # Current conversation info
    current_conv = get_current_conversation()
    if current_conv:
        st.info(f"📝 Current: {current_conv['name']}")

        # Rename current conversation
        with st.expander("✏️ Rename Current", expanded=False):
            new_name = st.text_input(
                "New Name",
                value=current_conv['name'],
                key="rename_input"
            )
            if st.button("Confirm Rename", key="confirm_rename"):
                if new_name.strip():
                    rename_conversation(current_conv['id'], new_name.strip())
                    st.rerun()

    st.divider()

    # Quick Settings
    st.markdown("#### 🎯 Quick Settings")

    # Destination
    current_conv = get_current_conversation()
    if current_conv:
        prefs = current_conv["preferences"]

        destination = st.text_input(
            "Destination",
            value=prefs.get("destination", ""),
            placeholder="e.g.: Tokyo"
        )
        if destination != prefs.get("destination", ""):
            prefs["destination"] = destination

        # Travel Dates
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            start_date = st.date_input(
                "Start Date",
                value=prefs.get("start_date", datetime.now().date())
            )
        with col_date2:
            end_date = st.date_input(
                "End Date",
                value=prefs.get("end_date", datetime.now().date())
            )

        prefs["start_date"] = start_date
        prefs["end_date"] = end_date

    st.divider()

    # About
    st.markdown("#### ℹ️ About")
    st.caption("""
    **TripPilot v2.0**  
    Intelligent Travel Planning Assistant  

    Powered by AI, providing flight, hotel, weather search and itinerary planning services.
    
    **New Features**
    - ✨ Multi-conversation management
    - 🚀 Performance optimization
    - 💾 Auto-save
    """)

    # Feedback
    if st.button("💬 Provide Feedback", use_container_width=True):
        st.info("Thank you for your feedback! Feature in development...")

# ==================== Footer ====================

st.markdown("---")
st.caption("TripPilot © 2025 | Powered by Deepseek & Claude AI")