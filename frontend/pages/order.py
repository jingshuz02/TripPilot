"""
Order Management Page - English Version with Data Visualization
Features:
1. ✅ Display all orders for current conversation
2. ✅ Data visualization (pie charts, bar charts, trend charts)
3. ✅ View order details
4. ✅ Delete orders with refund
5. ✅ Real-time budget statistics
"""

import streamlit as st
from datetime import datetime
from uuid import uuid4
import json
import os
import sys

# ==================== Path Configuration ====================
current_dir = os.path.dirname(__file__)
frontend_dir = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, frontend_dir)

# ==================== Check Plotly ====================
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# ==================== Page Configuration ====================
st.set_page_config(
    page_title="Order Management | TripPilot",
    page_icon="📋",
    layout="wide"
)

# ==================== Initialize Session State ====================
def init_session_state():
    """Initialize all necessary session states"""
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
                "orders": [],
                "total_spent": 0
            }
        }
        st.session_state.current_conversation_id = default_conv_id

    # Fix old conversation data structure
    for conv_id, conv in st.session_state.conversations.items():
        if "preferences" not in conv:
            conv["preferences"] = {
                "destination": conv.get("destination", ""),
                "days": conv.get("days", 3),
                "budget": conv.get("budget", 5000),
                "start_date": conv.get("start_date", datetime.now().date()),
                "end_date": conv.get("end_date", None)
            }
        if "orders" not in conv:
            conv["orders"] = []
        if "total_spent" not in conv:
            conv["total_spent"] = 0

    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]

init_session_state()

def get_current_conversation():
    """Get current conversation"""
    conv_id = st.session_state.current_conversation_id
    return st.session_state.conversations.get(conv_id)

def delete_order(order_id: str):
    """Delete order and refund"""
    current_conv = get_current_conversation()
    if not current_conv:
        return False

    orders = current_conv.get("orders", [])
    for order in orders:
        if order["id"] == order_id:
            refund_amount = order["price"]
            current_conv["total_spent"] = current_conv.get("total_spent", 0) - refund_amount
            orders.remove(order)
            current_conv["orders"] = orders
            st.success(f"✅ Order deleted, refunded ¥{refund_amount:,.0f}")
            return True
    return False

# ==================== Chart Creation Functions ====================
def create_budget_chart(total_budget, total_spent):
    """Create budget usage pie chart"""
    if not PLOTLY_AVAILABLE:
        return None

    remaining = max(0, total_budget - total_spent)

    fig = go.Figure(data=[go.Pie(
        labels=['Spent', 'Remaining'],
        values=[total_spent, remaining],
        hole=.3,
        marker_colors=['#ef4444', '#10b981'],
        textinfo='label+percent',
        textfont_size=14,
    )])

    fig.update_layout(
        title_text="Budget Usage",
        height=300,
        showlegend=True,
        margin=dict(t=40, b=20, l=20, r=20)
    )

    return fig

def create_order_type_chart(orders):
    """Create order type distribution pie chart"""
    if not PLOTLY_AVAILABLE or not orders:
        return None

    type_counts = {}
    type_labels = {"hotel": "🏨 Hotels", "flight": "✈️ Flights"}

    for order in orders:
        order_type = order.get("type", "unknown")
        label = type_labels.get(order_type, "Others")
        type_counts[label] = type_counts.get(label, 0) + 1

    fig = go.Figure(data=[go.Pie(
        labels=list(type_counts.keys()),
        values=list(type_counts.values()),
        hole=.3,
        marker_colors=['#3b82f6', '#f59e0b', '#8b5cf6'],
        textinfo='label+value',
        textfont_size=14,
    )])

    fig.update_layout(
        title_text="Order Type Distribution",
        height=300,
        showlegend=True,
        margin=dict(t=40, b=20, l=20, r=20)
    )

    return fig

def create_order_amount_chart(orders):
    """Create order amount bar chart"""
    if not PLOTLY_AVAILABLE or not orders:
        return None

    hotel_total = sum(o["price"] for o in orders if o.get("type") == "hotel")
    flight_total = sum(o["price"] for o in orders if o.get("type") == "flight")

    fig = go.Figure(data=[
        go.Bar(
            x=['🏨 Hotels', '✈️ Flights'],
            y=[hotel_total, flight_total],
            marker_color=['#3b82f6', '#f59e0b'],
            text=[f'¥{hotel_total:,.0f}', f'¥{flight_total:,.0f}'],
            textposition='auto',
        )
    ])

    fig.update_layout(
        title_text="Total Amount by Type",
        xaxis_title="Order Type",
        yaxis_title="Amount (¥)",
        height=300,
        showlegend=False,
        margin=dict(t=40, b=40, l=40, r=20)
    )

    return fig

def create_spending_trend_chart(orders):
    """Create spending trend line chart"""
    if not PLOTLY_AVAILABLE or not orders or len(orders) < 2:
        return None

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

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=dates,
        y=cumulative_spending,
        mode='lines+markers',
        name='Cumulative Spending',
        line=dict(color='#10b981', width=3),
        marker=dict(size=8)
    ))

    fig.update_layout(
        title_text="Spending Trend",
        xaxis_title="Date",
        yaxis_title="Cumulative Amount (¥)",
        height=300,
        showlegend=True,
        margin=dict(t=40, b=40, l=40, r=20)
    )

    return fig

# ==================== Styles ====================
st.markdown("""
<style>
    .order-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
    }
    
    .summary-card {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .summary-item {
        display: flex;
        justify-content: space-between;
        margin: 8px 0;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== Main Interface ====================
st.title("📋 Order Management")

# Get current conversation
current_conv = get_current_conversation()

if not current_conv:
    st.error("❌ Valid conversation not found")
    st.stop()

# Get order data
orders = current_conv.get("orders", [])

# Backward compatibility: try to read from global state
if not orders and "orders" in st.session_state:
    orders = st.session_state.get("orders", [])
    total_spent = st.session_state.get("total_spent", 0)
    # Prompt user to migrate
    st.warning("⚠️ Old data structure detected")
    if st.button("🔄 Migrate Data to Current Conversation", type="primary"):
        current_conv["orders"] = orders
        current_conv["total_spent"] = total_spent
        st.success("✅ Data migration successful!")
        st.rerun()
else:
    total_spent = current_conv.get("total_spent", 0)

total_budget = current_conv["preferences"].get("budget", 5000)
remaining = total_budget - total_spent

# ==================== Budget Summary Card ====================
st.markdown(f"""
<div class='summary-card'>
    <h3 style='margin-top: 0;'>💰 Budget Summary</h3>
    <div class='summary-item'>
        <span>Total Budget</span>
        <span style='font-size: 20px; font-weight: 700;'>¥{total_budget:,.0f}</span>
    </div>
    <div class='summary-item'>
        <span>Spent</span>
        <span style='font-size: 20px; font-weight: 700;'>¥{total_spent:,.0f}</span>
    </div>
    <div class='summary-item' style='border-top: 1px solid rgba(255,255,255,0.3); padding-top: 12px;'>
        <span>Remaining Budget</span>
        <span style='font-size: 24px; font-weight: 700;'>¥{remaining:,.0f}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== Statistics Cards ====================
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
if not PLOTLY_AVAILABLE:
    st.error("❌ Plotly not installed!")
    st.code("pip install plotly", language="bash")

elif not orders:
    st.info("📝 No order data available")
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
    st.subheader("📊 Data Analysis")

    # Create two rows of charts
    chart_row1_col1, chart_row1_col2 = st.columns(2)

    with chart_row1_col1:
        budget_chart = create_budget_chart(total_budget, total_spent)
        if budget_chart:
            st.plotly_chart(budget_chart, use_container_width=True, key="budget_chart")

    with chart_row1_col2:
        type_chart = create_order_type_chart(orders)
        if type_chart:
            st.plotly_chart(type_chart, use_container_width=True, key="type_chart")

    chart_row2_col1, chart_row2_col2 = st.columns(2)

    with chart_row2_col1:
        amount_chart = create_order_amount_chart(orders)
        if amount_chart:
            st.plotly_chart(amount_chart, use_container_width=True, key="amount_chart")

    with chart_row2_col2:
        trend_chart = create_spending_trend_chart(orders)
        if trend_chart:
            st.plotly_chart(trend_chart, use_container_width=True, key="trend_chart")
        else:
            st.info("📈 Insufficient orders to display trend chart (at least 2 orders required)")

st.divider()

# ==================== Order List ====================
if orders:
    st.subheader(f"📋 Order List ({len(orders)} items)")

    # Sort options
    col_sort1, col_sort2 = st.columns([3, 1])
    with col_sort2:
        sort_by = st.selectbox(
            "Sort",
            options=["Time (Newest)", "Time (Oldest)", "Price (High to Low)", "Price (Low to High)"],
            label_visibility="collapsed"
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
        status = order.get("status", "Paid")
        created_at = order.get("created_at", "N/A")
        item_details = order.get("item_details", {})

        icon = "🏨" if order_type == "hotel" else "✈️" if order_type == "flight" else "📦"

        with st.container():
            st.markdown(f"""
            <div class='order-card'>
                <div style='display: flex; justify-content: space-between; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 1px solid #e5e7eb;'>
                    <div>
                        <div style='font-size: 18px; font-weight: 600;'>{icon} {item_name}</div>
                        <div style='color: #6b7280; font-size: 13px; margin-top: 4px;'>Order Number: {order_id} | Created: {created_at}</div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-size: 24px; font-weight: 700; color: #10b981;'>¥{price:,.0f}</div>
                        <span style='display: inline-block; padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 500; background: #d1fae5; color: #065f46;'>{status}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

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
                    with col_d2:
                        st.write(f"**Destination**: {item_details.get('destination', 'N/A')}")
                        st.write(f"**Departure**: {item_details.get('departure_time', 'N/A')}")
                        st.write(f"**Cabin**: {item_details.get('cabin_class', 'N/A')}")

            col_btn1, col_btn2, col_btn3 = st.columns([4, 1, 1])
            with col_btn3:
                if st.button("🗑️ Delete", key=f"del_{order_id}_{idx}", use_container_width=True):
                    if delete_order(order_id):
                        st.rerun()

st.divider()

# ==================== Bottom Information ====================
col_footer1, col_footer2 = st.columns([3, 1])

with col_footer1:
    st.caption(f"📍 Current Conversation: **{current_conv['name']}** | Conversation ID: {current_conv['id']}")

with col_footer2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()