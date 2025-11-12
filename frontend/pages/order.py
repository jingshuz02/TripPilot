import streamlit as st
from datetime import datetime

# 页面标题
st.title("📋 My Orders & Trip Plans")

# 显示旅行计划和对应订单
st.header("📅 Trip Plans")
for trip in st.session_state.trips:
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(trip["name"])
            st.write(trip["desc"])
            st.caption(f"Created at: {trip['created_at']} | ID: {trip['id']}")
        
        # 订单列表
        st.subheader("📝 Orders")
        trip_orders = [o for o in st.session_state.orders if o.get('trip_id') == trip['id']]
        if trip_orders:
            for order in trip_orders:
                st.write(f"• {order['item']} - ${order['price']} ({order['time']}) | {order['status']}")
            total_spent_trip = sum(o['price'] for o in trip_orders)
            st.write(f"**Total Spent**: ${total_spent_trip}")
            
            # 清空订单按钮
            if st.button("Clear Order History", key=f"clear_order_{trip['id']}"):
                st.session_state.orders = [
                    o for o in st.session_state.orders 
                    if o.get('trip_id') != trip['id']
                ]
                st.rerun()
        else:
            st.markdown("""
                <div style="background-color: #e6f2ff; padding: 10px; border-radius: 5px;">
                    No orders yet
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()

# 预算状态
total_spent = sum(o['price'] for o in st.session_state.orders)
remaining = st.session_state.budget - total_spent
st.sidebar.metric(
    "Budget Status", 
    f"${remaining}", 
    f"Total: ${st.session_state.budget}"
)

# 侧边栏：预算设置
with st.sidebar:
    st.header("💰 Budget Settings")
    st.session_state.budget = st.number_input(
        "Update Budget (USD)", 
        min_value=0, 
        value=st.session_state.budget, 
        step=100
    )
    if st.button("Save Budget"):
        st.success("Budget updated!")
