import streamlit as st
import requests
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

st.set_page_config(
    page_title="TripPilot - Your Travel Assistant",
    page_icon="✈️",
    layout="wide"
)


# Initialize session state - 更安全的方式
def init_session_state():
    """Initialize all session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "api_connected" not in st.session_state:
        # Check backend connection
        try:
            response = requests.get("http://localhost:5000/health", timeout=2)
            st.session_state.api_connected = response.status_code == 200
        except Exception as e:
            st.session_state.api_connected = False
            print(f"Backend connection check failed: {e}")


# Call initialization
init_session_state()

# Main title
st.title("✈️ TripPilot - Intelligent Travel Planning Assistant")
st.caption("Powered by DeepSeek AI")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")

    # API status with refresh button
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
                st.rerun()
            except:
                st.session_state.api_connected = False
                st.rerun()

    if not st.session_state.api_connected:
        st.info("📝 Start backend:\n```\npython backend/app.py\n```")

    st.divider()

    # Travel preferences
    st.subheader("🎯 Travel Preferences")
    budget = st.number_input("Budget (USD)", min_value=0, value=1000, step=100)
    start_date = st.date_input("Departure Date", value=datetime.now())
    end_date = st.date_input("Return Date")
    language = st.selectbox("Language", ["English", "中文", "日本語"])

    st.divider()

    # Quick planning
    st.subheader("🗺️ Quick Planning")
    destination = st.text_input("Destination", placeholder="e.g., Tokyo, Paris, New York")
    preferences = st.text_area("Preferences", placeholder="e.g., History, Culture, Food, Nature")

    if st.button("Generate Itinerary", type="primary", disabled=not st.session_state.api_connected):
        if destination:
            with st.spinner("✨ Planning your perfect trip..."):
                try:
                    response = requests.post(
                        "http://localhost:5000/api/plan-trip",
                        json={
                            "destination": destination,
                            "start_date": str(start_date),
                            "end_date": str(end_date),
                            "budget": str(budget),
                            "preferences": preferences
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        plan = data.get("plan", "")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"📋 **Your {destination} Itinerary**\n\n{plan}"
                        })
                        st.rerun()
                    else:
                        st.error(f"❌ Planning failed: {response.text}")
                except requests.exceptions.Timeout:
                    st.error("⏱️ Request timeout, please try again")
                except requests.exceptions.ConnectionError:
                    st.error("🔌 Cannot connect to backend")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Please enter a destination")

    st.divider()

    # Clear conversation
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.subheader("💬 Chat with TripPilot")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input(
        "Ask me anything about travel..." if st.session_state.api_connected else "Backend not connected"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get assistant response
    if st.session_state.api_connected:
        with st.chat_message("assistant"):
            with st.spinner("🤔 Thinking..."):
                try:
                    # Prepare conversation history
                    history = [
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages[:-1]
                    ]

                    # Call backend API
                    response = requests.post(
                        "http://localhost:5000/api/chat",
                        json={
                            "message": prompt,
                            "history": history
                        },
                        timeout=30
                    )

                    if response.status_code == 200:
                        data = response.json()
                        assistant_message = data.get("message", "Sorry, I cannot answer this question.")
                        st.markdown(assistant_message)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message
                        })
                    else:
                        error_msg = f"❌ Error: {response.text}"
                        st.error(error_msg)
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })

                except requests.exceptions.Timeout:
                    error_msg = "⏱️ Request timeout, please try again"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                except requests.exceptions.ConnectionError:
                    error_msg = "🔌 Cannot connect to backend service"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
                except Exception as e:
                    error_msg = f"❌ Connection failed: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
    else:
        with st.chat_message("assistant"):
            error_msg = "❌ Backend service not connected. Please start the backend first:\n```bash\npython backend/app.py\n```"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

# Page footer info
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("💬 Conversation Turns", len(st.session_state.messages) // 2)
with col2:
    st.metric("💰 Budget", f"${budget}")
with col3:
    st.metric("🤖 LLM Model", "DeepSeek")