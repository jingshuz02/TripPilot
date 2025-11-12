import streamlit as st
import requests
from datetime import datetime
from uuid import uuid4

# --------------- Initialize all states first at the top ---------------
# Initialize API client (ensure priority over other states)
if "api_client" not in st.session_state:
    from api_client import APIClient  # Import APIClient
    st.session_state.api_client = APIClient()  # Instantiate

# Initialize multi-conversation state
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "conv_0": {
            "messages": [],  # Independent message list for each conversation
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }
if "active_conv_id" not in st.session_state:
    st.session_state.active_conv_id = "conv_0"

# Initialize API connection state
if "api_connected" not in st.session_state:
    st.session_state.api_connected = st.session_state.api_client.check_health()

# Ensure message list exists for current conversation
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
if "messages" not in current_conv:
    current_conv["messages"] = []

# --------------- Page Content ---------------
# Page title
st.title("💬 Chat with TripPilot")

# Sidebar (Conversation Management + All Orders + Settings)
with st.sidebar:
    # 1. Conversation Management Area
    st.header("🗨️ Conversation Management")
    # New Conversation Button
    if st.button("+ New Conversation", use_container_width=True):
        new_conv_id = f"conv_{len(st.session_state.conversations)}"
        st.session_state.conversations[new_conv_id] = {
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.active_conv_id = new_conv_id
        st.rerun()
    # Conversation List Selection
    conv_options = {
        conv_id: f"Conversation {i+1} ({data['created_at']})" 
        for i, (conv_id, data) in enumerate(st.session_state.conversations.items())
    }
    selected_conv_id = st.selectbox(
        "Select Conversation",
        options=list(conv_options.keys()),
        format_func=lambda x: conv_options[x],
        index=list(conv_options.keys()).index(st.session_state.active_conv_id)
    )
    if selected_conv_id != st.session_state.active_conv_id:
        st.session_state.active_conv_id = selected_conv_id
        st.rerun()
    st.divider()

    # Travel Preferences
    if "budget" not in st.session_state:
        st.session_state.budget = 1000  # Initialize budget
    st.session_state.budget = st.number_input(
        "Budget (USD)", 
        min_value=0, 
        value=st.session_state.budget, 
        step=100
    )
    start_date = st.date_input("Departure Date", value=datetime.now())
    end_date = st.date_input("Return Date")
    language = st.selectbox("Language", ["English", "Chinese", "日本語"])
    st.divider()
    # Clear Current Conversation
    if st.button("🗑️ Clear Current Conversation", use_container_width=True):
        st.session_state.conversations[st.session_state.active_conv_id]["messages"] = []
        st.rerun()
    st.divider()

    # 2. All Orders Display
    st.header("📋 All Order Records")
    if "orders" in st.session_state and st.session_state.orders:
        for order in st.session_state.orders:
            st.write(f"• {order['item']} - ${order['price']}")
            st.caption(f"Time: {order['time']} | Status: {order['status']}")
        total_spent = sum(o['price'] for o in st.session_state.orders)
        st.write(f"**Total Spent**: ${total_spent}")
    else:
        st.markdown("""
            <div style="background-color: #e6f2ff; padding: 10px; border-radius: 5px;">
                No orders yet
            </div>
            """, unsafe_allow_html=True)
    st.divider()

    # 3. Settings Area
    st.header("⚙️ Settings")
    # API Status
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.api_connected:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Disconnected")
    with col2:
        if st.button("🔄"):
            st.session_state.api_connected = st.session_state.api_client.check_health()
            st.rerun()
    if not st.session_state.api_connected:
        st.info("📝 Start backend:\n```\npython backend/app.py\n```")
    st.divider()

# --------------- Chat Content Display and Interaction ---------------
# Get messages of current conversation
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
messages = current_conv["messages"]

# Display message history of current conversation (ensure messages are initialized)
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle chat input
if prompt := st.chat_input("Please enter your travel needs... (e.g., Help me book a hotel in Tokyo for 3 nights)"):
    # Add user message to current conversation
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):
            # Hotel Booking Logic
            if "book hotel" in prompt or "reserve hotel" in prompt:
                city = "Tokyo" if "Tokyo" in prompt else "Default City"
                nights = 3 if "3 nights" in prompt else 2
                hotels = [
                    {
                        "name": f"{city} Central Hotel ({nights} nights)",
                        "price": 450 * nights,
                        "desc": f"Located in the city center of {city}, within walking distance to attractions, breakfast included"
                    },
                    {
                        "name": f"{city} Bay Hotel ({nights} nights)",
                        "price": 580 * nights,
                        "desc": f"Sea view room, free airport transfer, dinner included"
                    }
                ]
                response = f"Found {len(hotels)} hotel options in {city} for you:\n\n"
                for i, hotel in enumerate(hotels):
                    response += f"{i+1}. **{hotel['name']}**\n"
                    response += f"   Price: ${hotel['price']}\n"
                    response += f"   Description: {hotel['desc']}\n\n"
                response += "Please reply with the hotel number (1 or 2) to complete the booking"
                st.markdown(response)
                messages.append({"role": "assistant", "content": response})

            # Confirm Booking
            elif prompt.isdigit() and 1 <= int(prompt) <= 2:
                prev_msg = messages[-2]["content"] if len(messages) >= 2 else ""
                if "Central Hotel" in prev_msg:
                    selected_hotel = {"name": "Tokyo Central Hotel (3 nights)", "price": 1350}
                else:
                    selected_hotel = {"name": "Tokyo Bay Hotel (3 nights)", "price": 1740}
                # Initialize order list (prevent undefined)
                if "orders" not in st.session_state:
                    st.session_state.orders = []
                order_id = str(uuid4())[:8]
                st.session_state.orders.append({
                    "id": order_id,
                    "item": selected_hotel["name"],
                    "price": selected_hotel["price"],
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "trip_id": st.session_state.trips[0]["id"] if "trips" in st.session_state else "trip_0",
                    "status": "Booked"
                })
                response = f"✅ Booking Successful!\nOrder ID: {order_id}\nBooked Item: {selected_hotel['name']}\nTotal Price: ${selected_hotel['price']}"
                st.markdown(response)
                messages.append({"role": "assistant", "content": response})

            # Normal Conversation
            else:
                response = "I have received your request. Do you need help booking hotels, flights, or creating a travel plan?"
                st.markdown(response)
                messages.append({"role": "assistant", "content": response})

import streamlit as st
from datetime import datetime, timedelta
from uuid import uuid4

# --------------- Initialize Global State ---------------
# Initialize API Client
if "api_client" not in st.session_state:
    from api_client import APIClient
    st.session_state.api_client = APIClient()

# Initialize Multi-Converation Storage
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "conv_0": {
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
    }
if "active_conv_id" not in st.session_state:
    st.session_state.active_conv_id = "conv_0"

# Initialize Orders and Trips Data
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

# Initialize API Connection State
if "api_connected" not in st.session_state:
    st.session_state.api_connected = st.session_state.api_client.check_health()

# Ensure message list exists for current conversation
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
if "messages" not in current_conv:
    current_conv["messages"] = []

# --------------- Page Configuration ---------------
st.set_page_config(
    page_title="TripPilot - Chat",
    page_icon="💬",
    layout="wide"
)

# --------------- Page Title ---------------
st.title("💬 Chat with TripPilot")

# --------------- Sidebar ---------------
with st.sidebar:
    # 1. Conversation Management
    st.header("🗨️ Conversation Management")
    # New Conversation Button
    if st.button("+ New Conversation", use_container_width=True):
        new_conv_id = f"conv_{len(st.session_state.conversations)}"
        st.session_state.conversations[new_conv_id] = {
            "messages": [],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        st.session_state.active_conv_id = new_conv_id
        st.rerun()
    
    # Conversation Selection Dropdown
    conv_options = {
        conv_id: f"Conversation {i+1} ({data['created_at']})" 
        for i, (conv_id, data) in enumerate(st.session_state.conversations.items())
    }
    selected_conv_id = st.selectbox(
        "Select Conversation",
        options=list(conv_options.keys()),
        format_func=lambda x: conv_options[x],
        index=list(conv_options.keys()).index(st.session_state.active_conv_id)
    )
    if selected_conv_id != st.session_state.active_conv_id:
        st.session_state.active_conv_id = selected_conv_id
        st.rerun()
    st.divider()

    # 2. Travel Preferences Settings (to be sent to backend)
    st.header("🎯 Travel Preferences")
    budget = st.number_input(
        "Budget (USD)",
        min_value=0,
        value=st.session_state.budget,
        step=100,
        key="travel_budget"
    )
    start_date = st.date_input(
        "Departure Date",
        value=datetime.now(),
        key="start_date"
    )
    end_date = st.date_input(
        "Return Date",
        value=datetime.now() + timedelta(days=3),
        key="end_date"
    )
    language = st.selectbox(
        "Language",
        ["Chinese", "English", "日本語"],
        key="language"
    )
    
    # Package travel preferences into a dictionary
    travel_preferences = {
        "budget": budget,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "language": language
    }
    st.divider()

    # 3. Order Records Display
    st.header("📋 All Orders")
    if st.session_state.orders:
        for order in st.session_state.orders:
            st.write(f"• {order['item']} - ${order['price']}")
            st.caption(f"Time: {order['time']} | Status: {order['status']}")
        total_spent = sum(o['price'] for o in st.session_state.orders)
        st.write(f"**Total Spent**: ${total_spent}")
    else:
        st.info("No orders yet")
    st.divider()

    # 4. Backend Connection Status
    st.header("⚙️ Connection Status")
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.api_connected:
            st.success("Backend Connected")
        else:
            st.error("Backend Disconnected")
    with col2:
        if st.button("Refresh"):
            st.session_state.api_connected = st.session_state.api_client.check_health()
            st.rerun()
    if not st.session_state.api_connected:
        st.info("Please start the backend service: `python backend/app.py`")

# --------------- Chat Content Display and Interaction ---------------
# Get message list of current conversation
current_conv = st.session_state.conversations[st.session_state.active_conv_id]
messages = current_conv["messages"]

# Display historical messages
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle user input
if prompt := st.chat_input("Please enter your travel needs... (e.g., Help me book a hotel in Tokyo for 3 nights)"):
    # Add user message to current conversation
    messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)



    with st.chat_message("assistant"):
      with st.spinner("Processing..."):
          # Handle case when backend is not connected (terminate logic early)
          if not st.session_state.api_connected:
              error_msg = "Backend not connected. Please start the backend service first to use the function."
              st.error(error_msg)
              messages.append({"role": "assistant", "content": error_msg})
              # Use pass instead of continue to avoid syntax errors
              pass

          # Handle case when backend is connected
          else:
              # 1. Send user request and travel preferences to backend
              backend_response = st.session_state.api_client.send_travel_request(
                  prompt=prompt,
                  preferences=travel_preferences
              )

              # 2. Handle case where backend has no response
              if not backend_response:
                  no_response_msg = "No response from backend. Please try again later."
                  st.error(no_response_msg)
                  messages.append({"role": "assistant", "content": no_response_msg})
                  pass

              # 3. Handle backend response
              else:
                  action = backend_response.get("action")
                  params = backend_response.get("params", {})

                  # 3.1 Backend returns direct text reply
                  if action == "reply":
                      reply_content = backend_response.get("content", "Received your request.")
                      st.markdown(reply_content)
                      messages.append({"role": "assistant", "content": reply_content})

                  # 3.2 Backend instruction: Search for hotels
                  elif action == "search_hotels":
                      # Call hotel search API
                      hotels = st.session_state.api_client.search_hotels(
                          city=params.get("city", ""),
                          check_in=params.get("check_in", ""),
                          check_out=params.get("check_out", ""),
                          budget=travel_preferences["budget"]
                      )

                      # Handle search results
                      if not hotels or "hotels" not in hotels:
                          no_hotel_msg = "No hotels found matching your criteria."
                          st.error(no_hotel_msg)
                          messages.append({"role": "assistant", "content": no_hotel_msg})
                      else:
                          # Display hotel list
                          hotel_list_msg = "Found the following hotels for you:\n\n"
                          for i, hotel in enumerate(hotels["hotels"]):
                              hotel_list_msg += f"{i+1}. **{hotel['name']}**\n"
                              hotel_list_msg += f"   Price: ${hotel['price']}/night\n"
                              hotel_list_msg += f"   Address: {hotel['address']}\n"
                              hotel_list_msg += f"   Description: {hotel['desc']}\n\n"
                          hotel_list_msg += "Please reply with the hotel number (e.g., 1, 2) to complete the booking."
                          st.markdown(hotel_list_msg)
                          # Temporarily store hotel information for subsequent booking
                          messages.append({
                              "role": "assistant",
                              "content": hotel_list_msg,
                              "attached_hotels": hotels["hotels"]
                          })

                  # 3.3 Backend instruction: Confirm booking
                  elif action == "book_hotel":
                      # Call hotel booking API
                      booking_result = st.session_state.api_client.book_hotel(
                          hotel_id=params.get("hotel_id", ""),
                          trip_id=st.session_state.trips[0]["id"]
                      )

                      # Handle booking result
                      if booking_result and booking_result.get("status") == "success":
                          order_id = str(uuid4())[:8]
                          st.session_state.orders.append({
                              "id": order_id,
                              "item": booking_result["hotel_name"],
                              "price": booking_result["price"],
                              "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                              "trip_id": st.session_state.trips[0]["id"],
                              "status": "Booked"
                          })
                          success_msg = f"✅ Booking successful!\nOrder ID: {order_id}\nHotel: {booking_result['hotel_name']}\nTotal price: ${booking_result['price']}"
                          st.success(success_msg)
                          messages.append({"role": "assistant", "content": success_msg})
                      else:
                          fail_msg = "Booking failed. Please try again."
                          st.error(fail_msg)
                          messages.append({"role": "assistant", "content": fail_msg})

                  # 3.4 Handle unknown instructions
                  else:
                      default_msg = "Received your request. We are processing it..."
                      st.markdown(default_msg)
                      messages.append({"role": "assistant", "content": default_msg})

  
