"""
TripPilot Chat Interface - Enhanced Version (Adaptive Layout + Booking Confirmation Dialog)
New Features:
1. 💰 Unified budget management (not separate budgets for each type)
2. 📊 Real-time remaining budget display
3. 🔄 Optimized refresh logic to avoid double-clicking
4. 📱 Adaptive layout (content centers and expands when sidebar collapses) ✨ NEW
5. 🎯 Intelligent budget allocation recommendations
6. ✅ Booking confirmation dialog ✨ NEW - Shows detailed confirmation dialog after clicking booking
"""

import streamlit as st
import requests
from datetime import datetime, timedelta
import json
import sys
import os
import base64

# ✅ Fix path: add frontend directory to path
current_dir = os.path.dirname(__file__)  # frontend/pages/
frontend_dir = os.path.abspath(os.path.join(current_dir, '..'))  # frontend/
sys.path.insert(0, frontend_dir)

# ✅ Logo path configuration
icon_path = os.path.abspath(os.path.join(current_dir, "..", "images", "logo.jpg"))

# ==================== Import Custom Components ====================
try:
    from components.hotel_card import display_hotel_card_v2, display_hotel_list_v2
    print("✅ Successfully imported hotel_card_v2 component (with date picker)")
except ImportError as e:
    print(f"❌ Failed to import hotel component: {e}")
    display_hotel_list_v2 = None
    display_hotel_card_v2 = None

try:
    from components.weather_widget import display_weather_enhanced
    print("✅ Successfully imported weather component (with date picker)")
except ImportError as e:
    print(f"❌ Failed to import weather component: {e}")
    display_weather_enhanced = None

try:
    from components.flight_card import display_flight_card_v2, display_flight_list_v2
    print("✅ Successfully imported flight component (with date picker)")
except ImportError as e:
    print(f"❌ Failed to import flight component: {e}")
    display_flight_card_v2 = None
    display_flight_list_v2 = None

# ==================== Page Configuration ====================
st.set_page_config(
    page_title="TripPilot - Intelligent Travel Assistant",
    page_icon=icon_path if os.path.exists(icon_path) else "✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== Helper Functions ====================
def get_base64_image(image_path):
    """Convert image to base64 encoding for display in Markdown"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Image encoding failed: {e}")
        return ""  # Return empty on failure to avoid errors

# ==================== Initialize Session State ====================
def init_session_state():
    """Initialize all necessary session states"""
    from uuid import uuid4

    # ========== Conversation Management (unified data structure) ==========
    if "conversations" not in st.session_state:
        default_conv_id = str(uuid4())[:8]
        st.session_state.conversations = {
            default_conv_id: {
                "id": default_conv_id,
                "name": "New Conversation",
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "messages": [],
                "preferences": {
                    "destination": "",
                    "days": 3,
                    "budget": 5000,
                    "start_date": datetime.now().date(),
                    "end_date": None
                },
                "orders": [],  # ✅ Add orders array
                "total_spent": 0  # ✅ Add total spending
            }
        }
        st.session_state.current_conversation_id = default_conv_id

    # ✅ Fix old conversation data structure (backward compatibility)
    for conv_id, conv in st.session_state.conversations.items():
        if "preferences" not in conv:
            conv["preferences"] = {
                "destination": conv.get("destination", ""),
                "days": conv.get("days", 3),
                "budget": conv.get("budget", 5000),
                "start_date": conv.get("start_date", datetime.now().date()),
                "end_date": conv.get("end_date", None)
            }
        # ✅ Ensure each conversation has orders and total_spent fields
        if "orders" not in conv:
            conv["orders"] = []
        if "total_spent" not in conv:
            conv["total_spent"] = 0

        # Clean up old fields
        conv.pop("destination", None)
        conv.pop("start_date", None)
        conv.pop("end_date", None)
        conv.pop("days", None)
        conv.pop("budget", None)

    # Ensure current conversation ID is valid
    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]
    elif st.session_state.current_conversation_id not in st.session_state.conversations:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]

    # For backward compatibility
    current_conv = get_current_conversation()
    if current_conv:
        if "messages" not in st.session_state:
            st.session_state.messages = current_conv["messages"]
        if "current_trip" not in st.session_state:
            st.session_state.current_trip = current_conv["preferences"]

    # ✅ Unified budget management
    if "orders" not in st.session_state:
        st.session_state.orders = []

    if "total_spent" not in st.session_state:
        st.session_state.total_spent = 0

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = st.session_state.current_conversation_id

    # ✅ Add processing state to avoid duplicate processing
    if "processing" not in st.session_state:
        st.session_state.processing = False

    # ✅ Add last message ID to avoid duplicate triggers
    if "last_message_id" not in st.session_state:
        st.session_state.last_message_id = None

    # ✅ Add view state
    if "current_view" not in st.session_state:
        st.session_state.current_view = "chat"  # "chat" or "orders"

    # ✅ Add booking data state
    if "booking_data" not in st.session_state:
        st.session_state.booking_data = None


# ==================== Conversation Management Functions ====================

def create_new_conversation():
    """Create a new conversation"""
    from uuid import uuid4
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
        },
        "orders": [],  # ✅ Add orders array
        "total_spent": 0  # ✅ Add total spending
    }

    switch_conversation(new_conv_id)
    return new_conv_id


def switch_conversation(conv_id: str):
    """Switch conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.current_conversation_id = conv_id
        # Sync messages and preferences
        current_conv = st.session_state.conversations[conv_id]
        st.session_state.messages = current_conv["messages"]
        st.session_state.current_trip = current_conv["preferences"]
        st.session_state.conversation_id = conv_id


def delete_conversation(conv_id: str):
    """Delete conversation"""
    if len(st.session_state.conversations) <= 1:
        st.error("❌ Must keep at least one conversation")
        return False

    if conv_id in st.session_state.conversations:
        del st.session_state.conversations[conv_id]

        # If deleting current conversation, switch to first one
        if st.session_state.current_conversation_id == conv_id:
            first_conv_id = list(st.session_state.conversations.keys())[0]
            switch_conversation(first_conv_id)

        return True
    return False


def rename_conversation(conv_id: str, new_name: str):
    """Rename conversation"""
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["name"] = new_name
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        return True
    return False


def get_current_conversation():
    """Get current conversation"""
    conv_id = st.session_state.current_conversation_id
    return st.session_state.conversations.get(conv_id)


def update_conversation_timestamp():
    """Update current conversation timestamp"""
    conv_id = st.session_state.current_conversation_id
    if conv_id in st.session_state.conversations:
        st.session_state.conversations[conv_id]["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")


def save_message_to_conversation(role: str, content: str, **kwargs):
    """Save message to current conversation"""
    current_conv = get_current_conversation()
    if current_conv:
        message = {"role": role, "content": content, **kwargs}
        current_conv["messages"].append(message)
        st.session_state.messages = current_conv["messages"]
        update_conversation_timestamp()


# ✅ Helper function to calculate remaining budget
def get_remaining_budget():
    """Get current remaining budget"""
    current_conv = get_current_conversation()
    if current_conv:
        total_budget = current_conv["preferences"].get("budget", 5000)
        total_spent = current_conv.get("total_spent", 0)
        return total_budget - total_spent
    return 0


# ✅ Get budget recommendations
def get_budget_recommendations():
    """
    Give reasonable budget allocation recommendations based on trip days and remaining budget
    """
    current_conv = get_current_conversation()
    if not current_conv:
        return None

    total_budget = current_conv["preferences"].get("budget", 5000)
    days = current_conv["preferences"].get("days", 3)
    remaining = get_remaining_budget()

    # If more than half spent, give warning
    if remaining < total_budget * 0.5:
        percent_used = ((total_budget - remaining) / total_budget) * 100
        return {
            "status": "warning",
            "message": f"⚠️ {percent_used:.0f}% of budget used, please control spending"
        }

    # Suggested budget allocation (assuming not yet booked)
    if st.session_state.total_spent < 100:
        # Suggestion: Transportation 40%, Accommodation 30%, Other 30%
        suggested_flight = int(remaining * 0.4)
        suggested_hotel_total = int(remaining * 0.3)
        suggested_hotel_per_night = int(suggested_hotel_total / max(days - 1, 1))
        suggested_other = int(remaining * 0.3)

        return {
            "status": "info",
            "message": f"💡 Suggested Budget Allocation",
            "details": {
                "flight": f"Transportation: ¥{suggested_flight:,} (40%)",
                "hotel": f"Accommodation: ¥{suggested_hotel_per_night:,}/night",
                "other": f"Dining & Entertainment: ¥{suggested_other:,}"
            }
        }

    return None


# ==================== Booking Confirmation Dialog ✨ NEW ====================
@st.dialog("✅ Booking Confirmation", width="large")
def booking_confirmation_dialog(order_type: str, item: dict, price: float):
    """
    Booking confirmation dialog

    Parameters:
        order_type: Order type (flight/hotel)
        item: Item details
        price: Price
    """

    # Booking info card style
    st.markdown("""
    <style>
    .booking-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        padding: 25px;
        border-radius: 15px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .booking-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    .booking-price {
        font-size: 36px;
        font-weight: bold;
        margin: 15px 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .detail-item {
        background: rgba(255,255,255,0.1);
        padding: 10px 15px;
        border-radius: 8px;
        margin: 8px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Display different icons and names based on type
    icon_map = {
        "flight": "✈️",
        "hotel": "🏨"
    }
    type_name_map = {
        "flight": "Flight",
        "hotel": "Hotel"
    }
    icon = icon_map.get(order_type, "📦")
    type_name = type_name_map.get(order_type, "Service")

    # Get item name
    item_name = item.get('name', item.get('carrier_name', 'Unknown'))

    # Special handling for multiple hotel nights
    if order_type == 'hotel' and 'nights' in item:
        nights = item['nights']
        price_per_night = item.get('price', 0)
        display_name = f"{item_name} ({nights} nights @ ¥{price_per_night:,}/night)"
    else:
        display_name = item_name

    st.markdown(f"""
    <div class='booking-card'>
        <div class='booking-title'>{icon} {display_name}</div>
        <div style='font-size: 16px; opacity: 0.9;'>Booking Type: {type_name}</div>
        <div class='booking-price'>💰 ¥{price:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

    # Build detailed information
    details = {}

    if order_type == "flight":
        details = {
            "Airline": item.get('carrier_name', 'N/A'),
            "Flight Number": item.get('flight_number', 'N/A'),
            "Origin": item.get('origin', 'N/A'),
            "Destination": item.get('destination', 'N/A'),
            "Departure Time": item.get('departure_time', 'N/A'),
            "Arrival Time": item.get('arrival_time', 'N/A'),
            "Flight Duration": item.get('duration', 'N/A'),
            "Cabin Class": item.get('cabin_class', 'N/A')
        }
    elif order_type == "hotel":
        details = {
            "Hotel Name": item.get('name', 'N/A'),
            "Location": item.get('location', 'N/A'),
            "Address": item.get('address', 'N/A'),
            "Rating": f"{'⭐' * int(item.get('rating', 0))} ({item.get('rating', 0)})",
            "Amenities": ', '.join(item.get('amenities', [])) if item.get('amenities') else 'N/A'
        }

        if 'nights' in item:
            details["Nights"] = f"{item['nights']} nights"
            details["Price/Night"] = f"¥{item.get('price', 0):,}"

    # Display detailed information
    st.subheader("📋 Booking Details")

    col1, col2 = st.columns(2)
    items = list(details.items())
    mid = len(items) // 2 + len(items) % 2  # Round up

    with col1:
        for key, value in items[:mid]:
            st.markdown(f"""
            <div class='detail-item'>
                <strong>{key}</strong>: {value}
            </div>
            """, unsafe_allow_html=True)

    with col2:
        for key, value in items[mid:]:
            st.markdown(f"""
            <div class='detail-item'>
                <strong>{key}</strong>: {value}
            </div>
            """, unsafe_allow_html=True)

    st.divider()

    # Budget check
    total_budget = get_current_conversation()["preferences"].get("budget", 5000)
    remaining = get_remaining_budget()

    col_budget1, col_budget2, col_budget3 = st.columns(3)
    with col_budget1:
        st.metric("Total Budget", f"¥{total_budget:,.0f}")
    with col_budget2:
        st.metric("Used", f"¥{st.session_state.total_spent:,.0f}")
    with col_budget3:
        st.metric("Remaining Budget", f"¥{remaining:,.0f}")

    # Budget warning
    if price > remaining:
        st.error(f"❌ Insufficient budget! Need ¥{price:,.0f}, Remaining ¥{remaining:,.0f}")
        st.info("💡 Tip: You can adjust budget in the sidebar, or choose a lower-priced option.")
        if st.button("Close", type="secondary", use_container_width=True):
            st.session_state.booking_data = None
            st.rerun()
        return
    elif price > remaining * 0.8:
        st.warning(f"⚠️ This booking will use over 80% of remaining budget (Remaining ¥{remaining - price:,.0f})")

    st.divider()

    # Guest information form
    st.subheader("👤 Guest Information")

    with st.form("booking_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input(
                "Name *",
                placeholder="Please enter full name",
                help="Use name as shown on ID"
            )
            phone = st.text_input(
                "Phone *",
                placeholder="13800138000",
                help="For receiving booking confirmation"
            )

        with col2:
            email = st.text_input(
                "Email *",
                placeholder="example@email.com",
                help="Booking voucher will be sent to this email"
            )
            id_number = st.text_input(
                "ID Number *",
                placeholder="ID/Passport Number",
                help="Required for check-in/boarding procedures"
            )

        # Special requests
        if order_type == "flight":
            special_requests = st.multiselect(
                "Special Requests (Optional)",
                ["Wheelchair Service", "Special Meal", "Infant Bassinet", "Priority Boarding"],
                help="Select any special services needed"
            )
        elif order_type == "hotel":
            special_requests = st.multiselect(
                "Special Requests (Optional)",
                ["High Floor", "Non-Smoking Room", "Extra Bed", "Baby Cot", "Early Check-in", "Late Check-out"],
                help="Select your room preferences"
            )
        else:
            special_requests = []

        notes = st.text_area(
            "Other Notes (Optional)",
            placeholder="Any other special requests or notes",
            height=100
        )

        st.divider()

        # Terms of service
        agree = st.checkbox(
            "I have read and agree to the Terms of Service and Booking Policy",
            help="Check to agree to terms"
        )

        st.caption("📌 Note: Booking cannot be cancelled or modified after confirmation. Please verify all information before submitting.")

        st.divider()

        # Buttons
        col_btn1, col_btn2 = st.columns(2)

        with col_btn1:
            submit = st.form_submit_button(
                "✅ Confirm Booking",
                type="primary",
                use_container_width=True
            )

        with col_btn2:
            cancel = st.form_submit_button(
                "❌ Cancel",
                use_container_width=True
            )

        # Handle submission
        if submit:
            # Validate required fields
            if not all([name, phone, email, id_number]):
                st.error("❌ Please fill in all required fields (marked with *)")
            elif not agree:
                st.error("❌ Please agree to the Terms of Service first")
            else:
                # Simple validation
                if len(phone) < 11:
                    st.error("❌ Please enter a valid phone number")
                elif "@" not in email or "." not in email:
                    st.error("❌ Please enter a valid email address")
                else:
                    # Execute actual booking
                    from uuid import uuid4

                    order_id = f"ORD{uuid4().hex[:8].upper()}"
                    order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    # Build order details
                    item_details = {}
                    if order_type == "flight":
                        item_details = {
                            "carrier_name": item.get('carrier_name', 'N/A'),
                            "flight_number": item.get('flight_number', 'N/A'),
                            "origin": item.get('origin', 'N/A'),
                            "destination": item.get('destination', 'N/A'),
                            "departure_time": item.get('departure_time', 'N/A'),
                            "arrival_time": item.get('arrival_time', 'N/A'),
                            "duration": item.get('duration', 'N/A'),
                            "cabin_class": item.get('cabin_class', 'N/A')
                        }
                    elif order_type == "hotel":
                        item_details = {
                            "name": item.get('name', 'N/A'),
                            "location": item.get('location', 'N/A'),
                            "address": item.get('address', 'N/A'),
                            "rating": item.get('rating', 0),
                            "amenities": item.get('amenities', []),
                            "price": item.get('price', 0),  # Price per night
                            "nights": item.get('nights', 1),
                            "checkin_date": item.get('checkin_date', ''),
                            "checkout_date": item.get('checkout_date', '')
                        }

                    # Add order
                    order = {
                        "id": order_id,
                        "type": order_type,
                        "item_name": item_name,  # Add display name
                        "item": item,
                        "item_details": item_details,  # Add detailed info
                        "price": price,
                        "created_at": order_time,
                        "customer_name": name,
                        "customer_phone": phone,
                        "customer_email": email,
                        "customer_id": id_number,
                        "special_requests": special_requests if special_requests else [],
                        "notes": notes,
                        "status": "Paid"  # Changed to Paid
                    }

                    # ✅ Save to current conversation's orders
                    current_conv = get_current_conversation()
                    if current_conv:
                        if "orders" not in current_conv:
                            current_conv["orders"] = []
                        current_conv["orders"].append(order)

                        # Update conversation's total_spent
                        current_conv["total_spent"] = current_conv.get("total_spent", 0) + price

                    # Also update global orders and total_spent (backward compatibility)
                    if "orders" not in st.session_state:
                        st.session_state.orders = []
                    st.session_state.orders.append(order)
                    st.session_state.total_spent = st.session_state.get("total_spent", 0) + price

                    new_remaining = get_remaining_budget()

                    # Show success message
                    st.success(f"✅ Booking Successful!")
                    st.info(f"""
                    **Order Information**
                    - Order Number: `{order_id}`
                    - Booking Time: {order_time}
                    - Guest Name: {name}
                    - Contact: {phone}
                    - Amount Charged: ¥{price:,.0f}
                    - Remaining Budget: ¥{new_remaining:,.0f}
                    
                    Booking confirmation has been sent to {email}
                    """)

                    st.balloons()

                    # Clear booking data
                    st.session_state.booking_data = None

                    # Add confirmation message to chat
                    save_message_to_conversation(
                        "assistant",
                        f"🎉 Congratulations! Your {type_name} booking is confirmed!\n\nOrder Number: **{order_id}**\nBooking Item: {item_name}\nAmount: ¥{price:.2f}\n\nYou can view order details in the sidebar."
                    )

                    # Delay before closing
                    import time
                    time.sleep(2)
                    st.rerun()

        if cancel:
            st.session_state.booking_data = None
            st.rerun()


init_session_state()

# ==================== Style Definition - Light Green Theme with Responsive Layout ====================
st.markdown("""
<style>
    /* Overall Background */
    .stApp {
        background-color: #f8f9fa;
    }
    
    /* User Message Style - Light Green */
    .user-message {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 18px;
        padding: 12px 20px;
        margin: 10px 0;
        margin-left: 20%;
        box-shadow: 0 3px 15px rgba(16, 185, 129, 0.3);
        animation: fadeIn 0.3s ease-in;
    }
    
    /* AI Message Style */
    .ai-message {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 18px;
        padding: 15px 20px;
        margin: 10px 0;
        margin-right: 20%;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        line-height: 1.8;
        animation: fadeIn 0.3s ease-in;
    }
    
    /* Animation Effect */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Content Formatting */
    .ai-message h1 { color: #10b981; font-size: 1.5rem; margin: 1rem 0; }
    .ai-message h2 { color: #059669; font-size: 1.3rem; margin: 0.8rem 0; }
    .ai-message h3 { color: #047857; font-size: 1.1rem; margin: 0.6rem 0; }
    .ai-message strong { color: #047857; font-weight: 600; }
    .ai-message ul { margin: 0.5rem 0; padding-left: 1.5rem; }
    .ai-message li { margin: 0.3rem 0; line-height: 1.6; }
    
    /* ✅ Improved sidebar style - supports adaptive */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #6ee7b7 0%, #a7f3d0 100%);
        transition: all 0.3s ease;
    }
    
    /* Sidebar expanded state */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 350px !important;
        max-width: 500px !important;
    }
    
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 350px !important;
    }
    
    /* Sidebar collapsed state */
    [data-testid="stSidebar"][aria-expanded="false"] {
        min-width: 0 !important;
        max-width: 0 !important;
    }
    
    /* ✅✨ Main content area adaptive - key improvement: supports centered layout */
    .main .block-container {
        padding-left: 2rem;
        padding-right: 2rem;
        transition: all 0.3s ease;
    }
    
    /* When sidebar expanded - limit max width to maintain readability */
    section[data-testid="stSidebar"][aria-expanded="true"] ~ .main .block-container {
        max-width: 1200px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* ✨ When sidebar collapsed - expand and center */
    section[data-testid="stSidebar"][aria-expanded="false"] ~ .main .block-container {
        max-width: 1400px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 3rem;
        padding-right: 3rem;
    }
    
    /* ✅ Ensure main content container takes full width */
    .main {
        width: 100%;
    }
    
    /* ✅ Message container adaptive width */
    .stChatMessage {
        max-width: 100%;
    }
    
    /* Sidebar Text Color for Better Readability */
    [data-testid="stSidebar"] * {
        color: #065f46 !important;
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #065f46 !important;
    }
    
    [data-testid="stSidebar"] label {
        color: #047857 !important;
        font-weight: 500 !important;
    }
    
    /* Title Area */
    .main .block-container {
        padding-top: 2rem;
    }
    
    /* Sidebar Input Style */
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea,
    [data-testid="stSidebar"] select {
        background-color: white !important;
        border: 1px solid #10b981 !important;
        color: #111827 !important;
    }
    
    /* Sidebar Button Style */
    [data-testid="stSidebar"] button {
        background-color: white !important;
        color: #047857 !important;
        border: 1px solid #10b981 !important;
    }
    
    [data-testid="stSidebar"] button:hover {
        background-color: #10b981 !important;
        color: white !important;
    }
    
    /* Info Card */
    .info-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #10b981;
    }
    
    /* Button Style */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s;
        border: 1px solid #10b981;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
        background-color: #10b981;
        color: white;
    }
    
    /* Budget Warning Box */
    .budget-warning {
        background: #fef3c7;
        border: 2px solid #f59e0b;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #92400e;
        font-weight: 600;
    }
    
    .budget-danger {
        background: #fee2e2;
        border: 2px solid #ef4444;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #991b1b;
        font-weight: 600;
    }
    
    .budget-ok {
        background: #d1fae5;
        border: 2px solid #10b981;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        color: #065f46;
        font-weight: 600;
    }
    
    /* Sidebar Expander Style */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background-color: rgba(255, 255, 255, 0.7) !important;
        border: 1px solid #10b981 !important;
        border-radius: 8px !important;
        color: #047857 !important;
        font-weight: 600 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background-color: rgba(255, 255, 255, 0.9) !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderContent {
        background-color: rgba(255, 255, 255, 0.5) !important;
        border: 1px solid #a7f3d0 !important;
        border-top: none !important;
    }
    
    /* Primary Button Style */
    .stButton>button[kind="primary"] {
        background-color: #10b981;
        color: white;
    }
    
    .stButton>button[kind="primary"]:hover {
        background-color: #059669;
    }
    
    /* Sidebar Metric Style */
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.8);
        padding: 10px;
        border-radius: 8px;
        border: 1px solid #10b981;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: #047857 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: #065f46 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== API Interaction Functions ====================
def call_backend_api(message: str) -> dict:
    """Call backend API to get response - Optimized version"""
    try:
        trip = st.session_state.current_trip

        request_data = {
            "prompt": message,
            "preferences": {
                "budget": max(500, trip.get("budget", 5000)),
                "destination": trip.get("destination", ""),
                "days": max(1, trip.get("days", 3)),
                "start_date": str(trip.get("start_date", datetime.now().date())),
                "end_date": str(trip.get("end_date", "")),
                # ✅ Add remaining budget info
                "remaining_budget": get_remaining_budget()
            },
            "conversation_history": st.session_state.messages[-10:] if st.session_state.messages else []
        }

        response = requests.post(
            "http://localhost:5000/api/chat",
            json=request_data,
            timeout=90
        )

        if response.status_code == 200:
            return response.json()
        else:
            return {
                "action": "error",
                "content": f"Sorry, server returned error (Status code: {response.status_code})",
                "data": None,
                "suggestions": []
            }

    except requests.exceptions.Timeout:
        return {
            "action": "error",
            "content": "Sorry, request timed out. Please try again later.",
            "data": None,
            "suggestions": ["Resend message"]
        }
    except requests.exceptions.ConnectionError:
        return {
            "action": "error",
            "content": "Cannot connect to backend service. Please ensure the backend is running.",
            "data": None,
            "suggestions": ["Check backend service", "Try again"]
        }
    except Exception as e:
        return {
            "action": "error",
            "content": f"An error occurred: {str(e)}",
            "data": None,
            "suggestions": []
        }


# ==================== Message Display Functions ====================
def display_user_message(content: str):
    """Display user message"""
    st.markdown(f"""
    <div class="user-message">
        <strong>👤 You</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)


def display_ai_message(message: dict, msg_idx: int = 0):
    """Display AI message"""
    content = message.get("content", "")
    action = message.get("action", "")
    data = message.get("data", None)
    suggestions = message.get("suggestions", [])

    # AI message container
    st.markdown(f"""
    <div class="ai-message">
        <strong>🤖 AI Assistant</strong><br>
        {content}
    </div>
    """, unsafe_allow_html=True)

    # Display data cards
    if data:
        if action == "search_hotels" and isinstance(data, list):
            display_hotels(data, msg_idx)
        elif action == "search_flights" and isinstance(data, list):
            display_flights(data, msg_idx)
        elif action == "weather" and isinstance(data, dict):
            display_weather(data)

    # Display suggestions
    if suggestions:
        display_suggestions(suggestions, msg_idx)


def display_hotels(hotels: list, msg_idx: int):
    """Display hotel list with unified budget"""
    if display_hotel_list_v2:
        # ✅ hotel_card takes 2 parameters (hotel, price), we need to convert to 3 parameters (order_type, item, price)
        display_hotel_list_v2(
            hotels,
            message_id=msg_idx,
            on_book_callback=lambda hotel, price: handle_booking("hotel", hotel, price)
        )
    else:
        _display_hotels_fallback(hotels, msg_idx)


def _display_hotels_fallback(hotels: list, msg_idx: int):
    """Hotel fallback display"""
    st.subheader("🏨 Recommended Hotels")

    remaining = get_remaining_budget()
    st.info(f"💰 Remaining Budget: ¥{remaining:,.0f}")

    for idx, hotel in enumerate(hotels):
        price = hotel.get('price', 0)
        with st.expander(f"⭐ {hotel.get('name', 'Unknown')} - ¥{price}/night", expanded=idx == 0):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Location:** {hotel.get('location', 'N/A')}")
                st.write(f"**Address:** {hotel.get('address', 'N/A')}")
                st.write(f"**Rating:** {'⭐' * int(hotel.get('rating', 0))}")
                st.write(f"**Amenities:** {', '.join(hotel.get('amenities', []))}")
            with col2:
                st.metric("Price", f"¥{price}/night")

                # ✅ Check budget
                if price > remaining:
                    st.error("💰 Insufficient Budget")
                else:
                    if st.button(f"Book", key=f"book_hotel_{msg_idx}_{idx}"):
                        handle_booking("hotel", hotel, price)


def display_flights(flights: list, msg_idx: int):
    """Display flight list with unified budget"""
    if display_flight_list_v2:
        # ✅ Pass message ID and booking callback - accepts 3 parameters (order_type, item, price)
        display_flight_list_v2(
            flights,
            message_id=msg_idx,
            on_book_callback=handle_booking  # Pass function directly, it accepts 3 parameters
        )
    else:
        _display_flights_fallback(flights, msg_idx)


def _display_flights_fallback(flights: list, msg_idx: int):
    """Flight fallback display"""
    st.subheader("✈️ Recommended Flights")

    remaining = get_remaining_budget()
    st.info(f"💰 Remaining Budget: ¥{remaining:,.0f}")

    for idx, flight in enumerate(flights):
        price = flight.get('price', 0)
        with st.expander(
            f"{flight.get('carrier_name', 'Unknown')} {flight.get('flight_number', '')} - ¥{price}",
            expanded=idx == 0
        ):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Departure:** {flight.get('departure_time', '')}")
                st.write(f"**Origin:** {flight.get('origin', 'N/A')}")
            with col2:
                st.write(f"**Arrival:** {flight.get('arrival_time', '')}")
                st.write(f"**Destination:** {flight.get('destination', 'N/A')}")
            with col3:
                st.write(f"**Duration:** {flight.get('duration', 'N/A')}")
                st.write(f"**Class:** {flight.get('cabin_class', 'N/A')}")

            # ✅ Check budget
            if price > remaining:
                st.error("💰 Insufficient Budget")
            else:
                if st.button(f"Book", key=f"book_flight_{msg_idx}_{idx}"):
                    handle_booking("flight", flight, price)


def display_weather(weather: dict):
    """Display weather information"""
    if display_weather_enhanced:
        formatted_weather = {
            "location": weather.get("location", weather.get("city", "")),
            "temperature": weather.get("temperature", 0),
            "feels_like": weather.get("feels_like", 0),
            "weather": weather.get("weather", ""),
            "description": weather.get("description", ""),
            "humidity": weather.get("humidity", 0),
            "wind_speed": weather.get("wind_speed", ""),
            "wind_direction": weather.get("wind_direction", ""),
            "visibility": weather.get("visibility", ""),
            "pressure": weather.get("pressure", ""),
            "uv_index": weather.get("uv_index", 0),
            "sunrise": weather.get("sunrise", ""),
            "sunset": weather.get("sunset", ""),
            "update_time": weather.get("update_time", ""),
            "forecast": weather.get("forecast", [])
        }
        display_weather_enhanced(formatted_weather)
    else:
        _display_weather_fallback(weather)


def _display_weather_fallback(weather: dict):
    """Weather fallback display"""
    with st.container():
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Temperature", f"{weather.get('temperature', 'N/A')}°C")
        with col2:
            st.metric("Humidity", f"{weather.get('humidity', 'N/A')}%")
        with col3:
            st.metric("Wind Speed", weather.get('wind_speed', 'N/A'))
        with col4:
            st.metric("Weather", weather.get('weather', 'N/A'))


# ==================== Suggestion Buttons ====================
def display_suggestions(suggestions: list, msg_idx: int = 0):
    """Display suggestion buttons"""
    if not suggestions:
        return

    st.markdown("**You might also want to know:**")
    cols = st.columns(min(len(suggestions[:3]), 3))
    for idx, (col, suggestion) in enumerate(zip(cols, suggestions[:3])):
        with col:
            button_key = f"sug_{msg_idx}_{idx}_{suggestion[:20]}"
            if st.button(f"{suggestion}", key=button_key):
                st.session_state.pending_message = suggestion
                st.rerun()


# ==================== Orders View with Data Visualization ====================
def display_orders_view():
    """Display order management view with charts"""

    # Back to chat button
    col_nav1, col_nav2 = st.columns([1, 5])
    with col_nav1:
        if st.button("← Back to Chat", use_container_width=True):
            st.session_state.current_view = "chat"
            st.rerun()

    st.title("📋 Order Management")

    current_conv = get_current_conversation()
    if not current_conv:
        st.error("❌ Current conversation not found")
        return

    # Show current conversation name
    st.info(f"📍 Current Conversation: **{current_conv['name']}**")

    # Get order data
    orders = current_conv.get("orders", [])
    total_spent = current_conv.get("total_spent", 0)
    total_budget = current_conv["preferences"].get("budget", 5000)
    remaining = total_budget - total_spent

    # Top summary card
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border-radius: 12px; padding: 20px; margin-bottom: 20px;">
        <h3 style='margin: 0 0 16px 0;'>💰 Budget Overview</h3>
        <div style='display: flex; justify-content: space-between; padding: 8px 0;'>
            <span>Total Budget</span>
            <span style='font-size: 20px; font-weight: 700;'>¥{total_budget:,.0f}</span>
        </div>
        <div style='display: flex; justify-content: space-between; padding: 8px 0;'>
            <span>Spent</span>
            <span style='font-size: 20px; font-weight: 700;'>¥{total_spent:,.0f}</span>
        </div>
        <div style='display: flex; justify-content: space-between; padding: 12px 0; border-top: 1px solid rgba(255,255,255,0.3);'>
            <span>Remaining Budget</span>
            <span style='font-size: 24px; font-weight: 700;'>¥{remaining:,.0f}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📦 Total Orders", len(orders))
    with col2:
        hotel_orders = [o for o in orders if o.get("type") == "hotel"]
        st.metric("🏨 Hotel Orders", len(hotel_orders))
    with col3:
        flight_orders = [o for o in orders if o.get("type") == "flight"]
        st.metric("✈️ Flight Orders", len(flight_orders))
    with col4:
        usage_percent = (total_spent / total_budget * 100) if total_budget > 0 else 0
        st.metric("📊 Budget Usage", f"{usage_percent:.1f}%")

    # Budget progress bar
    if total_budget > 0:
        progress = min(total_spent / total_budget, 1.0)
        st.progress(progress)

    st.divider()

    # ==================== 📊 Data Visualization Area ====================
    if not orders:
        st.info("📝 No orders yet")
        st.markdown("""
        ### 💡 Tips
        - Search for hotels or flights in the chat interface
        - Select suitable options and complete booking
        - Orders will automatically appear on this page
        """)

        # Provide test data option
        if st.button("🧪 Load Test Data (Demo Only)", type="primary"):
            test_orders = [
                {
                    "id": "TEST001",
                    "type": "hotel",
                    "item_name": "Chengdu Oriental Plaza NUO Hotel",
                    "price": 1440,
                    "created_at": "2025-11-22 10:30:00",
                    "status": "Paid",
                    "item_details": {
                        "name": "Chengdu Oriental Plaza NUO Hotel",
                        "location": "Jinjiang District, Chengdu",
                        "rating": 4.8,
                        "nights": 2
                    }
                },
                {
                    "id": "TEST002",
                    "type": "hotel",
                    "item_name": "Chengdu Times Garden Hotel",
                    "price": 1460,
                    "created_at": "2025-11-23 14:20:00",
                    "status": "Paid",
                    "item_details": {
                        "name": "Chengdu Times Garden Hotel",
                        "location": "Wuhou District, Chengdu",
                        "rating": 4.7,
                        "nights": 2
                    }
                }
            ]
            current_conv["orders"] = test_orders
            current_conv["total_spent"] = 2900
            st.success("✅ Test data loaded!")
            st.rerun()

    else:
        # ==================== Show Charts ====================
        st.subheader("📊 Data Analysis")

        try:
            import plotly.graph_objects as go

            # Create two rows of charts
            chart_row1_col1, chart_row1_col2 = st.columns(2)

            with chart_row1_col1:
                # Chart 1: Budget Usage Pie Chart
                remaining_amt = max(0, total_budget - total_spent)

                fig1 = go.Figure(data=[go.Pie(
                    labels=['Spent', 'Remaining'],
                    values=[total_spent, remaining_amt],
                    hole=.3,
                    marker_colors=['#ef4444', '#10b981'],
                    textinfo='label+percent',
                    textfont_size=14,
                )])

                fig1.update_layout(
                    title_text="Budget Usage",
                    height=300,
                    showlegend=True,
                    margin=dict(t=40, b=20, l=20, r=20)
                )

                st.plotly_chart(fig1, use_container_width=True, key="budget_chart")

            with chart_row1_col2:
                # Chart 2: Order Type Distribution
                type_counts = {}
                type_labels = {"hotel": "🏨 Hotels", "flight": "✈️ Flights"}

                for order in orders:
                    order_type = order.get("type", "unknown")
                    label = type_labels.get(order_type, "Others")
                    type_counts[label] = type_counts.get(label, 0) + 1

                fig2 = go.Figure(data=[go.Pie(
                    labels=list(type_counts.keys()),
                    values=list(type_counts.values()),
                    hole=.3,
                    marker_colors=['#3b82f6', '#f59e0b', '#8b5cf6'],
                    textinfo='label+value',
                    textfont_size=14,
                )])

                fig2.update_layout(
                    title_text="Order Type Distribution",
                    height=300,
                    showlegend=True,
                    margin=dict(t=40, b=20, l=20, r=20)
                )

                st.plotly_chart(fig2, use_container_width=True, key="type_chart")

            chart_row2_col1, chart_row2_col2 = st.columns(2)

            with chart_row2_col1:
                # Chart 3: Order Amount Bar Chart
                hotel_total = sum(o["price"] for o in orders if o.get("type") == "hotel")
                flight_total = sum(o["price"] for o in orders if o.get("type") == "flight")

                fig3 = go.Figure(data=[
                    go.Bar(
                        x=['🏨 Hotels', '✈️ Flights'],
                        y=[hotel_total, flight_total],
                        marker_color=['#3b82f6', '#f59e0b'],
                        text=[f'¥{hotel_total:,.0f}', f'¥{flight_total:,.0f}'],
                        textposition='auto',
                    )
                ])

                fig3.update_layout(
                    title_text="Total Amount by Type",
                    xaxis_title="Order Type",
                    yaxis_title="Amount (¥)",
                    height=300,
                    showlegend=False,
                    margin=dict(t=40, b=40, l=40, r=20)
                )

                st.plotly_chart(fig3, use_container_width=True, key="amount_chart")

            with chart_row2_col2:
                # Chart 4: Spending Trend
                if len(orders) >= 2:
                    sorted_orders = sorted(orders, key=lambda x: x.get("created_at", ""))

                    dates = []
                    cumulative_spending = []
                    current_total = 0

                    for order in sorted_orders:
                        created_at = order.get("created_at", "")
                        if created_at:
                            date_str = created_at.split()[0] if " " in created_at else created_at[:10]
                            dates.append(date_str)
                            current_total += order.get("price", 0)
                            cumulative_spending.append(current_total)

                    fig4 = go.Figure()

                    fig4.add_trace(go.Scatter(
                        x=dates,
                        y=cumulative_spending,
                        mode='lines+markers',
                        name='Cumulative Spending',
                        line=dict(color='#10b981', width=3),
                        marker=dict(size=8)
                    ))

                    fig4.update_layout(
                        title_text="Spending Trend",
                        xaxis_title="Date",
                        yaxis_title="Cumulative Amount (¥)",
                        height=300,
                        showlegend=True,
                        margin=dict(t=40, b=40, l=40, r=20)
                    )

                    st.plotly_chart(fig4, use_container_width=True, key="trend_chart")
                else:
                    st.info("📈 Insufficient orders to display trend chart (at least 2 orders required)")

        except ImportError:
            st.warning("⚠️ Plotly not installed. Charts cannot be displayed.")
            st.code("pip install plotly", language="bash")
        except Exception as e:
            st.error(f"❌ Chart generation error: {str(e)}")

        st.divider()

        # ==================== Order List ====================
        st.subheader(f"📋 Order List ({len(orders)} items)")

        # Sort options
        col_sort1, col_sort2 = st.columns([3, 1])
        with col_sort2:
            sort_by = st.selectbox(
                "Sort",
                options=["Time (Newest)", "Time (Oldest)", "Price (High to Low)", "Price (Low to High)"],
                label_visibility="collapsed",
                key="order_sort"
            )

        # Sort
        sorted_orders = orders.copy()
        if sort_by == "Time (Newest)":
            sorted_orders.reverse()
        elif sort_by == "Price (High to Low)":
            sorted_orders.sort(key=lambda x: x.get("price", 0), reverse=True)
        elif sort_by == "Price (Low to High)":
            sorted_orders.sort(key=lambda x: x.get("price", 0))

        # Display orders
        for idx, order in enumerate(sorted_orders, 1):
            order_type = order.get("type", "unknown")
            item_name = order.get("item_name", "Unknown Item")
            price = order.get("price", 0)
            order_id = order.get("id", "N/A")
            status = order.get("status", "Unknown")
            created_at = order.get("created_at", "N/A")
            item_details = order.get("item_details", {})

            # Order icon
            icon = "🏨" if order_type == "hotel" else "✈️" if order_type == "flight" else "📦"

            # Status color
            if status == "Paid":
                status_style = "background: #d1fae5; color: #065f46;"
            elif status == "Pending":
                status_style = "background: #fef3c7; color: #92400e;"
            else:
                status_style = "background: #fee2e2; color: #991b1b;"

            with st.container():
                st.markdown(f"""
                <div style="background: white; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin-bottom: 16px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #e5e7eb;">
                        <div>
                            <div style="font-size: 18px; font-weight: 600;">{icon} {item_name}</div>
                            <div style="color: #6b7280; font-size: 13px; margin-top: 4px;">Order Number: {order_id} | Created: {created_at}</div>
                        </div>
                        <div style="text-align: right;">
                            <div style="font-size: 24px; font-weight: 700; color: #10b981;">¥{price:,.0f}</div>
                            <span style="display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; {status_style}">{status}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Order details expander
                with st.expander("📄 View Details"):
                    if order_type == "hotel":
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            st.write(f"**Hotel Name**: {item_details.get('name', 'N/A')}")
                            st.write(f"**Location**: {item_details.get('location', 'N/A')}")
                            st.write(f"**Rating**: {item_details.get('rating', 'N/A')}/5.0")
                        with col_d2:
                            price_per_night = item_details.get('price', 0)
                            st.write(f"**Price/Night**: ¥{price_per_night:,.0f}")
                            amenities = item_details.get('amenities', [])
                            if amenities:
                                st.write(f"**Amenities**: {', '.join(amenities[:5])}")

                    elif order_type == "flight":
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                            st.write(f"**Airline**: {item_details.get('carrier_name', 'N/A')}")
                            st.write(f"**Flight Number**: {item_details.get('flight_number', 'N/A')}")
                            st.write(f"**Origin**: {item_details.get('origin', 'N/A')}")
                            st.write(f"**Destination**: {item_details.get('destination', 'N/A')}")
                        with col_d2:
                            st.write(f"**Departure Time**: {item_details.get('departure_time', 'N/A')}")
                            st.write(f"**Arrival Time**: {item_details.get('arrival_time', 'N/A')}")
                            st.write(f"**Flight Duration**: {item_details.get('duration', 'N/A')}")
                            st.write(f"**Cabin**: {item_details.get('cabin_class', 'N/A')}")

                    # Guest information
                    st.divider()
                    st.markdown("**👤 Guest Information**")
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        st.write(f"**Name**: {order.get('customer_name', 'N/A')}")
                        st.write(f"**Phone**: {order.get('customer_phone', 'N/A')}")
                    with col_c2:
                        st.write(f"**Email**: {order.get('customer_email', 'N/A')}")
                        st.write(f"**ID Number**: {order.get('customer_id', 'N/A')}")

                    # Special requests
                    special_requests = order.get('special_requests', [])
                    if special_requests:
                        st.write(f"**Special Requests**: {', '.join(special_requests)}")

                    # Notes
                    notes = order.get('notes', '')
                    if notes:
                        st.write(f"**Notes**: {notes}")

                # Action buttons
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
                with col_btn1:
                    if st.button("🗑️ Delete", key=f"del_{order_id}", use_container_width=True):
                        # Delete order and refund
                        current_conv["total_spent"] = current_conv.get("total_spent", 0) - price
                        orders.remove(order)
                        current_conv["orders"] = orders
                        st.success(f"✅ Order deleted, refunded ¥{price:,.0f}")
                        st.rerun()

                with col_btn2:
                    if st.button("📧 Email", key=f"email_{order_id}", use_container_width=True):
                        st.info(f"✉️ Order confirmation email sent to {order.get('customer_email', 'N/A')}")

    st.divider()

    # Bottom operations
    st.subheader("🛠️ Operations")
    col_op1, col_op2 = st.columns(2)

    with col_op1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    with col_op2:
        if orders and st.button("🗑️ Clear All Orders", use_container_width=True, type="secondary"):
            if st.checkbox("⚠️ Confirm clear all orders (cannot be undone)", key="confirm_clear_orders"):
                current_conv["orders"] = []
                current_conv["total_spent"] = 0
                st.success("✅ All orders cleared")
                st.rerun()

# ✅ Modified booking handling function - use session_state to delay dialog trigger
def handle_booking(order_type: str, item: dict, price: float):
    """
    Booking handling function - save booking data to session_state
    """
    # Save booking data to session_state, trigger dialog in main loop
    st.session_state.booking_data = {
        "order_type": order_type,
        "item": item,
        "price": price
    }


# ==================== Main Function ====================
def handle_user_input(message: str):
    """Handle user input"""
    if not message.strip():
        return

    if st.session_state.processing:
        return

    st.session_state.processing = True

    try:
        save_message_to_conversation("user", message)

        status_placeholder = st.empty()
        status_placeholder.info("🤔 AI is thinking, please wait...")

        response = call_backend_api(message)
        status_placeholder.empty()

        save_message_to_conversation(
            "assistant",
            response.get("content", ""),
            action=response.get("action"),
            data=response.get("data"),
            suggestions=response.get("suggestions", [])
        )

    finally:
        st.session_state.processing = False
        st.rerun()


# ==================== Sidebar ====================
with st.sidebar:
    # Use Markdown syntax to combine image and title text
    st.markdown(
        f"""
        <div style="display: flex; align-items: center; gap: 8px;">
            <img src="data:image/jpg;base64,{get_base64_image(icon_path)}" width="24"/>
            <h3 style="margin: 0;">Conversation Management</h3>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("➕ New Conversation", use_container_width=True, type="primary", key="new_conv_btn"):
            create_new_conversation()
            st.rerun()

    with col2:
        if st.button("🔄", use_container_width=True, help="Refresh", key="refresh_btn"):
            st.rerun()

    st.divider()

    # ✅ Real-time budget display - in most visible position
    st.markdown("### 💰 Budget Management")

    current_conv = get_current_conversation()
    if current_conv:
        total_budget = current_conv["preferences"].get("budget", 5000)
        total_spent = current_conv.get("total_spent", 0)  # Read from conversation
        remaining = get_remaining_budget()
        usage_percent = (total_spent / total_budget * 100) if total_budget > 0 else 0

        # Budget progress bar
        st.progress(min(usage_percent / 100, 1.0))

        # Budget metrics
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.metric(
                "Total Budget",
                f"¥{total_budget:,.0f}",
                delta=None
            )
        with col_b2:
            st.metric(
                "Remaining",
                f"¥{remaining:,.0f}",
                delta=f"-¥{total_spent:,.0f}" if total_spent > 0 else None,
                delta_color="inverse"
            )

        # Budget status alert
        if remaining < 0:
            st.markdown(f"""
            <div class="budget-danger">
                ⚠️ Over budget by ¥{abs(remaining):,.0f}
            </div>
            """, unsafe_allow_html=True)
        elif remaining < total_budget * 0.2:
            st.markdown(f"""
            <div class="budget-warning">
                ⚠️ Budget almost used ({usage_percent:.1f}% spent)
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="budget-ok">
                ✅ Sufficient budget ({usage_percent:.1f}% spent)
            </div>
            """, unsafe_allow_html=True)

        conv_orders = current_conv.get("orders", [])
        st.caption(f"Spent: ¥{total_spent:,.0f} | Orders: {len(conv_orders)}")

        # ✅ Display budget recommendations
        budget_rec = get_budget_recommendations()
        if budget_rec:
            with st.expander("💡 Budget Recommendations", expanded=False):
                st.markdown(f"**{budget_rec['message']}**")
                if 'details' in budget_rec:
                    for key, value in budget_rec['details'].items():
                        st.caption(value)

    st.divider()

    # Conversation list
    st.markdown("#### 📋 Conversation List")

    sorted_convs = sorted(
        st.session_state.conversations.items(),
        key=lambda x: x[1]["updated_at"],
        reverse=True
    )

    for conv_id, conv in sorted_convs:
        is_active = conv_id == st.session_state.current_conversation_id
        msg_count = len(conv["messages"])

        with st.expander(
            f"{'🟢' if is_active else '⚪'} {conv['name']} ({msg_count} msgs)",
            expanded=is_active
        ):
            # Only show update time
            st.caption(f"Updated: {conv['updated_at']}")

            # Show order statistics
            conv_orders = conv.get("orders", [])
            conv_spent = conv.get("total_spent", 0)
            if conv_orders:
                st.caption(f"📦 Orders: {len(conv_orders)} | 💰 Spent: ¥{conv_spent:,.0f}")

            # Button row 1: Switch and Orders
            col_a, col_b = st.columns(2)

            with col_a:
                if not is_active:
                    if st.button("🔄 Switch", key=f"switch_{conv_id}", use_container_width=True):
                        switch_conversation(conv_id)
                        st.rerun()
                else:
                    st.button("🟢 Active", key=f"active_{conv_id}", use_container_width=True, disabled=True)

            with col_b:
                if st.button("📊 Orders", key=f"orders_{conv_id}", use_container_width=True):
                    # First switch to this conversation
                    if not is_active:
                        switch_conversation(conv_id)
                    # Switch to orders view
                    st.session_state.current_view = "orders"
                    st.rerun()

            # Button row 2: Rename and Delete
            col_c, col_d = st.columns(2)

            with col_c:
                if st.button("✏️ Rename", key=f"rename_{conv_id}", use_container_width=True):
                    st.session_state[f"renaming_{conv_id}"] = True
                    st.rerun()

            with col_d:
                if len(st.session_state.conversations) > 1:
                    if st.button("🗑️ Delete", key=f"delete_{conv_id}", use_container_width=True, type="secondary"):
                        if delete_conversation(conv_id):
                            st.success("✅ Deleted")
                            st.rerun()
                else:
                    st.button("🗑️ Delete", key=f"delete_disabled_{conv_id}", use_container_width=True, disabled=True)

            if st.session_state.get(f"renaming_{conv_id}", False):
                new_name = st.text_input(
                    "New Name",
                    value=conv['name'],
                    key=f"new_name_{conv_id}"
                )
                col_x, col_y = st.columns(2)
                with col_x:
                    if st.button("Confirm", key=f"confirm_{conv_id}", use_container_width=True):
                        if new_name.strip():
                            rename_conversation(conv_id, new_name.strip())
                            st.session_state[f"renaming_{conv_id}"] = False
                            st.rerun()
                with col_y:
                    if st.button("Cancel", key=f"cancel_{conv_id}", use_container_width=True):
                        st.session_state[f"renaming_{conv_id}"] = False
                        st.rerun()

    st.divider()

    # Current conversation settings
    st.markdown("#### ⚙️ Trip Preferences")

    current_conv = get_current_conversation()
    if current_conv:
        preferences = current_conv["preferences"]

        destination = st.text_input(
            "Destination",
            value=preferences.get("destination", ""),
            key="sidebar_destination"
        )
        preferences["destination"] = destination

        col1, col2 = st.columns(2)
        with col1:
            days = st.number_input(
                "Days",
                min_value=1,
                max_value=30,
                value=max(1, preferences.get("days", 3)),
                step=1,
                key="sidebar_days"
            )
            preferences["days"] = days

        with col2:
            budget = st.number_input(
                "Budget (¥)",
                min_value=500,
                max_value=100000,
                value=max(500, int(preferences.get("budget", 5000))),
                step=500,
                key="sidebar_budget"
            )
            preferences["budget"] = budget

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=preferences.get("start_date", datetime.now().date()),
                min_value=datetime.now().date(),
                key="sidebar_start_date"
            )
            preferences["start_date"] = start_date

        with col2:
            default_end = start_date + timedelta(days=days-1)
            end_date = st.date_input(
                "End Date",
                value=default_end,
                min_value=start_date,
                key="sidebar_end_date"
            )
            preferences["end_date"] = end_date

        st.session_state.current_trip = preferences

    st.divider()

    st.subheader("Quick Actions")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Clear Current", use_container_width=True, key="clear_btn"):
            current_conv = get_current_conversation()
            if current_conv:
                current_conv["messages"] = []
                st.session_state.messages = []
                # ✅ Reset budget and orders when clearing
                current_conv["total_spent"] = 0
                current_conv["orders"] = []
                st.success("Cleared")
                st.rerun()

    with col2:
        if st.button("View Orders", use_container_width=True, key="view_orders_btn"):
            # Switch to orders view
            st.session_state.current_view = "orders"
            st.rerun()

    current_conv = get_current_conversation()
    conv_orders = current_conv.get("orders", []) if current_conv else []

    if conv_orders:
        with st.expander(f"Order Details ({len(conv_orders)})", expanded=False):
            for idx, order in enumerate(conv_orders, 1):
                item = order.get('item', {})
                order_type = order.get('type')
                item_name = order.get('item_name', item.get('name', item.get('carrier_name', 'Unknown')))
                price = order.get('price', 0)

                # Show order details
                st.markdown(f"**{idx}. {order.get('id', 'N/A')}**")

                if order_type == 'hotel' and 'nights' in item:
                    nights = item['nights']
                    st.write(f"🏨 {item_name} ({nights} nights)")
                else:
                    st.write(f"{'✈️' if order_type == 'flight' else '🏨'} {item_name}")

                st.caption(f"Amount: ¥{price:,.0f}")
                st.caption(f"Guest: {order.get('customer_name', 'N/A')}")
                st.caption(f"Time: {order.get('created_at', 'N/A')}")
                st.caption(f"Status: {order.get('status', 'Confirmed')}")

                if st.button("Delete", key=f"del_order_{idx}"):
                    current_conv["total_spent"] = current_conv.get("total_spent", 0) - price
                    conv_orders.pop(idx-1)
                    current_conv["orders"] = conv_orders
                    st.rerun()

                if idx < len(conv_orders):
                    st.divider()

    st.divider()

    # Status info
    current_conv = get_current_conversation()
    if current_conv:
        total_spent = current_conv.get("total_spent", 0)
        st.caption(f"""
        **Current Status**
        - Conversation: {current_conv['name']}
        - Messages: {len(current_conv['messages'])}
        - Destination: {current_conv['preferences'].get('destination') or 'Not set'}
        - Budget: ¥{current_conv['preferences'].get('budget', 0):,}
        - Spent: ¥{total_spent:,}
        - Days: {current_conv['preferences'].get('days', 0)}
        """)

    st.divider()

    # Backend status
    try:
        response = requests.get("http://localhost:5000/health", timeout=1)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Not Started")
        st.caption("Run: `python app.py`")


# ==================== Main Interface ====================

# ✅ View switcher
current_view = st.session_state.get("current_view", "chat")

if current_view == "orders":
    # ==================== Orders View ====================
    display_orders_view()
else:
    # ==================== Chat View ====================

    # Title with Logo
    if os.path.exists(icon_path):
        logo_base64 = get_base64_image(icon_path)
        if logo_base64:
            st.markdown(
                f"""
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 10px;">
                    <img src="data:image/jpg;base64,{logo_base64}" 
                         style="width: 50px; height: 50px; border-radius: 10px; 
                                box-shadow: 0 2px 8px rgba(0,0,0,0.1);"/>
                    <div>
                        <h1 style="margin: 0; font-size: 2rem;">TripPilot - Intelligent Travel Assistant</h1>
                        <p style="margin: 0; color: #6b7280; font-size: 0.9rem;">
                            Powered by AI | Make Travel Planning Simple and Fun
                        </p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.title("✈️ TripPilot - Intelligent Travel Assistant")
    else:
        st.title("✈️ TripPilot - Intelligent Travel Assistant")

    st.caption("Based on DeepSeek AI | Adaptive Layout + Booking Confirmation Dialog")

    # Display budget at top
    current_conv = get_current_conversation()
    if current_conv:
        total_budget = current_conv["preferences"].get("budget", 5000)
        remaining = get_remaining_budget()

        col_top1, col_top2, col_top3 = st.columns([2, 1, 1])
        with col_top1:
            st.info(f"📍 Current: **{current_conv['name']}** | {len(current_conv['messages'])} messages")
        with col_top2:
            st.metric("💰 Total Budget", f"¥{total_budget:,.0f}")
        with col_top3:
            delta_color = "normal" if remaining >= 0 else "inverse"
            st.metric("Remaining", f"¥{remaining:,.0f}", delta_color=delta_color)

    if not st.session_state.messages:
        st.markdown("""
        <div class="info-card">
        <h3>Hello! I'm your dedicated AI travel assistant</h3>
        <p>I can provide you with personalized travel services, including itinerary planning, hotel recommendations, flight inquiries, and more.</p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            **Itinerary Planning**
            - Detailed daily arrangements
            - Attraction route optimization
            - Time allocation suggestions
            """)

        with col2:
            st.markdown("""
            **Accommodation Recommendations**
            - Various hotel grade options
            - Location advantage analysis
            - Value-for-money ranking
            """)

        with col3:
            st.markdown("""
            **Transportation Arrangement**
            - Flight schedule inquiry
            - Optimal route recommendations
            - Transportation tool suggestions
            """)

        st.divider()

        st.subheader("Quick Start - Click to Try")

        example_queries = [
            "Help me plan a 3-day trip to Chengdu with a budget of 5000 yuan",
            "Recommend hotels near West Lake in Hangzhou",
            "Query flights from Beijing to Shanghai",
            "What are the must-see attractions in Tokyo?",
            "What's the weather like in Sanya, what clothes should I bring?"
        ]

        cols = st.columns(2)
        for idx, query in enumerate(example_queries):
            with cols[idx % 2]:
                if st.button(f"{query}", key=f"example_query_{idx}", use_container_width=True):
                    st.session_state.pending_message = query
                    st.rerun()

        st.divider()

        st.info("**Tip**: You can directly tell me your travel needs in the input box below!")

    # Display message history
    message_container = st.container()
    with message_container:
        for msg_idx, message in enumerate(st.session_state.messages):
            if message["role"] == "user":
                display_user_message(message["content"])
            else:
                display_ai_message(message, msg_idx)

    # ✅ Check if there's pending booking data, if so trigger dialog
    if st.session_state.booking_data:
        booking_data = st.session_state.booking_data
        booking_confirmation_dialog(
            order_type=booking_data["order_type"],
            item=booking_data["item"],
            price=booking_data["price"]
        )

    # Handle pending message
    if "pending_message" in st.session_state and st.session_state.pending_message:
        pending_msg = st.session_state.pending_message
        st.session_state.pending_message = None
        handle_user_input(pending_msg)

    # Input box
    user_input = st.chat_input(
        "Tell me your travel needs...",
        key="chat_input"
    )

    if user_input:
        handle_user_input(user_input)

    # Footer
    with st.container():
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.caption("✈️ TripPilot v2.4 - Your Intelligent Travel Partner (With Booking Confirmation)")

        with col2:
            if st.session_state.messages:
                last_msg_time = datetime.now().strftime("%H:%M")
                st.caption(f"Last updated: {last_msg_time}")
