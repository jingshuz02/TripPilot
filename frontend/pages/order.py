"""
修复版订单页面
修复内容：
1. 初始化session_state，避免AttributeError
2. 添加预算实时计算
3. 优化订单展示
"""

import streamlit as st
from datetime import datetime
from uuid import uuid4

# ==================== 初始化Session State ====================

def init_session_state():
    """初始化所有必要的session state"""
    if "trips" not in st.session_state:
        st.session_state.trips = [{
            "name": "我的旅行计划",
            "desc": "自动创建的默认行程",
            "id": str(uuid4())[:8],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "destination": "",
            "start_date": "",
            "end_date": ""
        }]

    if "orders" not in st.session_state:
        st.session_state.orders = []

    if "budget" not in st.session_state:
        st.session_state.budget = 5000

    if "current_payment" not in st.session_state:
        st.session_state.current_payment = None

# 调用初始化
init_session_state()

# ==================== 页面配置 ====================

st.title("📋 我的订单")
st.caption("查看和管理您的旅行订单")

# ==================== 订单统计 ====================

# 计算总花费
total_spent = sum(o['price'] for o in st.session_state.orders)
remaining = st.session_state.budget - total_spent

# 顶部统计卡片
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "订单总数",
        len(st.session_state.orders),
        delta=None
    )

with col2:
    flights = [o for o in st.session_state.orders if o['type'] == 'flight']
    st.metric(
        "✈️ 航班",
        len(flights),
        delta=None
    )

with col3:
    hotels = [o for o in st.session_state.orders if o['type'] == 'hotel']
    st.metric(
        "🏨 酒店",
        len(hotels),
        delta=None
    )

with col4:
    # 显示剩余预算，根据正负显示不同颜色
    st.metric(
        "剩余预算",
        f"¥{remaining:.2f}",
        delta=f"-¥{total_spent:.2f}" if total_spent > 0 else None,
        delta_color="inverse"
    )

# 预算使用进度条
if st.session_state.budget > 0:
    budget_usage = min(total_spent / st.session_state.budget, 1.0)
    st.progress(budget_usage)

    # 预算状态提示
    if remaining < 0:
        st.error(f"⚠️ 预算超支 ¥{abs(remaining):.2f}")
    elif remaining < st.session_state.budget * 0.2:
        st.warning(f"⚠️ 预算即将用完，剩余 ¥{remaining:.2f}")
    else:
        st.success(f"✅ 预算充足，剩余 ¥{remaining:.2f}")

st.divider()

# ==================== 按行程展示订单 ====================

if not st.session_state.trips:
    st.warning("暂无行程，请先创建行程")
else:
    for trip in st.session_state.trips:
        with st.expander(f"🗺️ {trip['name']}", expanded=True):
            # 行程信息
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                st.caption(f"📅 创建时间: {trip['created_at']}")
            with col_info2:
                st.caption(f"🆔 行程ID: {trip['id']}")

            if trip.get('desc'):
                st.write(trip['desc'])

            st.divider()

            # 获取该行程的订单
            trip_orders = [o for o in st.session_state.orders if o.get('trip_id') == trip['id']]

            if not trip_orders:
                st.info("📝 该行程暂无订单")
            else:
                st.markdown(f"**📝 订单列表** ({len(trip_orders)} 个)")

                # 显示订单
                for order in trip_orders:
                    with st.container(border=True):
                        col1, col2, col3, col4 = st.columns([4, 2, 2, 1])

                        with col1:
                            # 订单类型图标
                            icon = "✈️" if order['type'] == 'flight' else "🏨"

                            # 订单名称
                            st.markdown(f"**{icon} {order['item']}**")

                            # 订单ID和时间
                            st.caption(f"订单号: {order['id']}")
                            st.caption(f"创建时间: {order['time']}")

                        with col2:
                            # 价格
                            st.metric("金额", f"¥{order['price']:.2f}")

                        with col3:
                            # 状态
                            status_map = {
                                'Pending': ('⏳', 'Pending', 'orange'),
                                'Confirmed': ('✅', 'Confirmed', 'green'),
                                'Cancelled': ('❌', 'Cancelled', 'red')
                            }

                            status = order.get('status', 'Pending')
                            emoji, text, color = status_map.get(status, ('❓', status, 'gray'))

                            st.write(f"{emoji} {text}")

                            # 状态切换按钮
                            if status == 'Pending':
                                if st.button(
                                        "确认订单",
                                        key=f"confirm_{order['id']}",
                                        use_container_width=True
                                ):
                                    order['status'] = 'Confirmed'
                                    st.success("✅ 订单已确认！")
                                    st.rerun()

                        with col4:
                            # 删除按钮
                            if st.button(
                                    "🗑️",
                                    key=f"delete_{order['id']}",
                                    help="删除订单",
                                    use_container_width=True
                            ):
                                st.session_state.orders.remove(order)
                                st.success("✅ 订单已删除")
                                st.rerun()

                        # 详情展开
                        with st.expander("查看详细信息"):
                            details = order.get('details', {})

                            if order['type'] == 'flight':
                                col_d1, col_d2 = st.columns(2)

                                with col_d1:
                                    st.write(f"**起飞**: {details.get('departure_time', details.get('departure', 'N/A'))}")
                                    st.write(f"**到达**: {details.get('arrival_time', details.get('arrival', 'N/A'))}")
                                    st.write(f"**舱位**: {details.get('cabin_class', 'N/A')}")

                                with col_d2:
                                    st.write(f"**航空公司**: {details.get('operating_carrier', details.get('carrier_code', 'N/A'))}")
                                    st.write(f"**航班号**: {details.get('flight_number', 'N/A')}")
                                    st.write(f"**飞行时长**: {details.get('duration', 'N/A')}")

                            elif order['type'] == 'hotel':
                                col_d1, col_d2 = st.columns(2)

                                with col_d1:
                                    st.write(f"**酒店**: {details.get('name', 'N/A')}")
                                    st.write(f"**位置**: {details.get('location', 'N/A')}")
                                    st.write(f"**评分**: {details.get('rating', 'N/A')}/5.0")

                                with col_d2:
                                    st.write(f"**价格/晚**: ¥{details.get('price', 0):.2f}")
                                    desc = details.get('desc', '')
                                    if desc:
                                        st.write(f"**描述**: {desc[:100]}...")

                                    # 显示设施
                                    amenities = details.get('amenities', [])
                                    if amenities:
                                        st.write(f"**设施**: {', '.join(amenities[:3])}")

                # 该行程小计
                trip_total = sum(o['price'] for o in trip_orders)
                st.divider()
                st.markdown(f"**该行程总计**: ¥{trip_total:.2f}")

                # 清空该行程订单按钮
                if st.button(
                        "🗑️ 清空该行程的所有订单",
                        key=f"clear_trip_{trip['id']}",
                        type="secondary"
                ):
                    st.session_state.orders = [
                        o for o in st.session_state.orders
                        if o.get('trip_id') != trip['id']
                    ]
                    st.success("✅ 已清空该行程的订单")
                    st.rerun()

st.divider()

# ==================== 全局操作 ====================

st.markdown("### 🛠️ 订单管理")

col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    if st.button("🔄 刷新订单", use_container_width=True):
        st.rerun()

with col_btn2:
    # 导出订单为JSON
    if st.button("📊 导出订单数据", use_container_width=True):
        if st.session_state.orders:
            import json
            orders_json = json.dumps(st.session_state.orders, ensure_ascii=False, indent=2)
            st.download_button(
                label="下载订单JSON",
                data=orders_json,
                file_name=f"orders_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        else:
            st.info("暂无订单可导出")

with col_btn3:
    if st.button("🗑️ 清空所有订单", use_container_width=True, type="secondary"):
        if st.session_state.orders:
            if st.checkbox("确认清空所有订单", key="confirm_clear_all"):
                st.session_state.orders = []
                st.success("✅ 所有订单已清空")
                st.rerun()
        else:
            st.info("暂无订单可清空")

# ==================== 侧边栏预算管理 ====================

with st.sidebar:
    st.header("💰 预算管理")

    # 预算使用进度
    if st.session_state.budget > 0:
        progress = min(total_spent / st.session_state.budget, 1.0)
        st.progress(progress)

        # 进度百分比
        usage_percent = (total_spent / st.session_state.budget) * 100
        st.caption(f"已使用 {usage_percent:.1f}%")

    st.metric(
        "剩余预算",
        f"¥{remaining:.2f}",
        delta=f"已用: ¥{total_spent:.2f}",
        delta_color="inverse"
    )

    st.divider()

    # 预算设置
    st.markdown("### 📝 预算设置")

    new_budget = st.number_input(
        "更新预算 (¥)",
        min_value=0,
        value=st.session_state.budget,
        step=100,
        key="budget_update"
    )

    if st.button("💾 保存预算", use_container_width=True, type="primary"):
        st.session_state.budget = new_budget
        st.success("✅ 预算已更新！")
        st.rerun()

    st.divider()

    # 快速统计
    st.markdown("### 📊 快速统计")

    if st.session_state.orders:
        # 按类型统计
        flight_cost = sum(o['price'] for o in st.session_state.orders if o['type'] == 'flight')
        hotel_cost = sum(o['price'] for o in st.session_state.orders if o['type'] == 'hotel')

        st.write(f"✈️ 航班费用: ¥{flight_cost:.2f}")
        st.write(f"🏨 酒店费用: ¥{hotel_cost:.2f}")

        # 按状态统计
        pending = len([o for o in st.session_state.orders if o.get('status') == 'Pending'])
        confirmed = len([o for o in st.session_state.orders if o.get('status') == 'Confirmed'])

        st.write(f"⏳ 待确认: {pending} 个")
        st.write(f"✅ 已确认: {confirmed} 个")

    st.divider()

    # 快速导航
    st.markdown("### 🧭 快速导航")
    if st.button("💬 返回聊天", use_container_width=True):
        st.switch_page("pages/chat.py")

    if st.button("🏠 返回首页", use_container_width=True):
        st.switch_page("frontend/streamlit_app.py")

# ==================== 底部说明 ====================

st.markdown("---")
st.caption("💡 提示：订单数据保存在当前会话中，关闭浏览器后将丢失")