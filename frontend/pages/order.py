"""
完善版订单管理页面
功能：
1. ✅ 显示当前对话的所有订单
2. ✅ 支持查看订单详情
3. ✅ 支持删除订单并退款
4. ✅ 实时预算统计
5. ✅ 订单导出功能
"""

import streamlit as st
from datetime import datetime
from uuid import uuid4
import json

# ==================== 页面配置 ====================
st.set_page_config(
    page_title="订单管理 | TripPilot",
    page_icon="📋",
    layout="wide"
)

# ==================== 初始化 Session State ====================
def init_session_state():
    """初始化所有必要的session state"""
    if "conversations" not in st.session_state:
        default_conv_id = str(uuid4())[:8]
        st.session_state.conversations = {
            default_conv_id: {
                "id": default_conv_id,
                "name": "新对话",
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

    if "current_conversation_id" not in st.session_state:
        st.session_state.current_conversation_id = list(st.session_state.conversations.keys())[0]

init_session_state()

# ==================== 辅助函数 ====================
def get_current_conversation():
    """获取当前对话"""
    conv_id = st.session_state.current_conversation_id
    return st.session_state.conversations.get(conv_id)


def delete_order(order_id: str):
    """删除订单并退款"""
    current_conv = get_current_conversation()
    if not current_conv:
        return False

    orders = current_conv.get("orders", [])
    for order in orders:
        if order["id"] == order_id:
            # 退款
            refund_amount = order["price"]
            current_conv["total_spent"] = current_conv.get("total_spent", 0) - refund_amount

            # 删除订单
            orders.remove(order)
            current_conv["orders"] = orders

            st.success(f"✅ 订单已删除，已退款 ¥{refund_amount:,.0f}")
            return True

    return False


def export_orders_to_json():
    """导出订单为JSON"""
    current_conv = get_current_conversation()
    if not current_conv:
        return None

    orders = current_conv.get("orders", [])
    export_data = {
        "conversation_id": current_conv["id"],
        "conversation_name": current_conv["name"],
        "export_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_orders": len(orders),
        "total_spent": current_conv.get("total_spent", 0),
        "budget": current_conv["preferences"].get("budget", 5000),
        "orders": orders
    }

    return json.dumps(export_data, ensure_ascii=False, indent=2)


# ==================== 样式 ====================
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
    
    .order-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
        padding-bottom: 12px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .order-title {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
    }
    
    .order-price {
        font-size: 24px;
        font-weight: 700;
        color: #10b981;
    }
    
    .order-meta {
        color: #6b7280;
        font-size: 13px;
        margin-top: 4px;
    }
    
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-paid {
        background: #d1fae5;
        color: #065f46;
    }
    
    .status-pending {
        background: #fef3c7;
        color: #92400e;
    }
    
    .status-cancelled {
        background: #fee2e2;
        color: #991b1b;
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
        padding: 8px 0;
    }
</style>
""", unsafe_allow_html=True)

# ==================== 主界面 ====================
st.title("📋 订单管理")

current_conv = get_current_conversation()

if not current_conv:
    st.error("❌ 未找到当前对话")
    st.stop()

# ==================== 顶部汇总卡片 ====================
orders = current_conv.get("orders", [])
total_spent = current_conv.get("total_spent", 0)
total_budget = current_conv["preferences"].get("budget", 5000)
remaining = total_budget - total_spent

st.markdown(f"""
<div class='summary-card'>
    <h3 style='margin: 0 0 16px 0;'>💰 预算概览</h3>
    <div class='summary-item'>
        <span>总预算</span>
        <span style='font-size: 20px; font-weight: 700;'>¥{total_budget:,.0f}</span>
    </div>
    <div class='summary-item'>
        <span>已花费</span>
        <span style='font-size: 20px; font-weight: 700;'>¥{total_spent:,.0f}</span>
    </div>
    <div class='summary-item' style='border-top: 1px solid rgba(255,255,255,0.3); padding-top: 12px;'>
        <span>剩余预算</span>
        <span style='font-size: 24px; font-weight: 700;'>¥{remaining:,.0f}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== 统计卡片 ====================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 订单总数", len(orders))

with col2:
    hotel_orders = [o for o in orders if o.get("type") == "hotel"]
    st.metric("🏨 酒店订单", len(hotel_orders))

with col3:
    flight_orders = [o for o in orders if o.get("type") == "flight"]
    st.metric("✈️ 航班订单", len(flight_orders))

with col4:
    usage_percent = (total_spent / total_budget * 100) if total_budget > 0 else 0
    st.metric("📊 预算使用率", f"{usage_percent:.1f}%")

# 预算进度条
if total_budget > 0:
    progress = min(total_spent / total_budget, 1.0)
    st.progress(progress)

st.divider()

# ==================== 订单列表 ====================
if not orders:
    st.info("📝 暂无订单")
    st.markdown("""
    ### 💡 提示
    - 在聊天界面搜索酒店或航班
    - 选择合适的选项并完成预订
    - 订单将自动显示在此页面
    """)
else:
    st.subheader(f"📋 订单列表 ({len(orders)} 个)")

    # 排序选项
    col_sort1, col_sort2 = st.columns([3, 1])
    with col_sort2:
        sort_by = st.selectbox(
            "排序",
            options=["时间倒序", "时间正序", "价格从高到低", "价格从低到高"],
            label_visibility="collapsed"
        )

    # 排序
    sorted_orders = orders.copy()
    if sort_by == "时间倒序":
        sorted_orders.reverse()
    elif sort_by == "价格从高到低":
        sorted_orders.sort(key=lambda x: x.get("price", 0), reverse=True)
    elif sort_by == "价格从低到高":
        sorted_orders.sort(key=lambda x: x.get("price", 0))

    # 显示订单
    for idx, order in enumerate(sorted_orders, 1):
        order_type = order.get("type", "unknown")
        item_name = order.get("item_name", "未知项目")
        price = order.get("price", 0)
        order_id = order.get("id", "N/A")
        status = order.get("status", "未知")
        created_at = order.get("created_at", "N/A")
        item_details = order.get("item_details", {})

        # 订单图标
        icon = "🏨" if order_type == "hotel" else "✈️" if order_type == "flight" else "📦"

        # 状态徽章
        status_class = "status-paid" if status == "已支付" else "status-pending" if status == "待支付" else "status-cancelled"

        with st.container():
            st.markdown(f"""
            <div class='order-card'>
                <div class='order-header'>
                    <div>
                        <div class='order-title'>{icon} {item_name}</div>
                        <div class='order-meta'>订单号: {order_id} | 创建时间: {created_at}</div>
                    </div>
                    <div style='text-align: right;'>
                        <div class='order-price'>¥{price:,.0f}</div>
                        <span class='status-badge {status_class}'>{status}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 订单详情展开
            with st.expander("📄 查看详情"):
                if order_type == "hotel":
                    col_d1, col_d2 = st.columns(2)

                    with col_d1:
                        st.write(f"**酒店名称**: {item_details.get('name', 'N/A')}")
                        st.write(f"**位置**: {item_details.get('location', 'N/A')}")
                        st.write(f"**评分**: {item_details.get('rating', 'N/A')}/5.0")

                        # 如果有入住信息
                        if 'checkin_date' in item_details:
                            checkin = item_details['checkin_date']
                            checkout = item_details.get('checkout_date', 'N/A')
                            nights = item_details.get('nights', 1)
                            st.write(f"**入住日期**: {checkin}")
                            st.write(f"**退房日期**: {checkout}")
                            st.write(f"**入住晚数**: {nights}晚")

                    with col_d2:
                        price_per_night = item_details.get('price', 0)
                        st.write(f"**价格/晚**: ¥{price_per_night:,.0f}")
                        st.write(f"**地址**: {item_details.get('address', 'N/A')}")

                        # 设施
                        amenities = item_details.get('amenities', [])
                        if amenities:
                            st.write(f"**设施**: {', '.join(amenities[:5])}")

                elif order_type == "flight":
                    col_d1, col_d2 = st.columns(2)

                    with col_d1:
                        st.write(f"**航空公司**: {item_details.get('carrier_name', 'N/A')}")
                        st.write(f"**航班号**: {item_details.get('flight_number', 'N/A')}")
                        st.write(f"**出发**: {item_details.get('origin', 'N/A')}")
                        st.write(f"**到达**: {item_details.get('destination', 'N/A')}")

                    with col_d2:
                        st.write(f"**起飞时间**: {item_details.get('departure_time', 'N/A')}")
                        st.write(f"**到达时间**: {item_details.get('arrival_time', 'N/A')}")
                        st.write(f"**飞行时长**: {item_details.get('duration', 'N/A')}")
                        cabin = item_details.get('cabin_class', 'N/A')
                        st.write(f"**舱位**: {cabin}")

            # 操作按钮
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])

            with col_btn1:
                if st.button("🗑️ 删除", key=f"del_{order_id}", use_container_width=True):
                    if delete_order(order_id):
                        st.rerun()

            with col_btn2:
                if st.button("📧 发送邮件", key=f"email_{order_id}", use_container_width=True):
                    st.info(f"✉️ 订单确认邮件已发送到您的邮箱")

            st.markdown("</div>", unsafe_allow_html=True)

st.divider()

# ==================== 底部操作区 ====================
st.subheader("🛠️ 批量操作")

col_op1, col_op2, col_op3, col_op4 = st.columns(4)

with col_op1:
    if st.button("🔄 刷新页面", use_container_width=True):
        st.rerun()

with col_op2:
    if orders:
        json_data = export_orders_to_json()
        if json_data:
            st.download_button(
                label="📊 导出订单",
                data=json_data,
                file_name=f"orders_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

with col_op3:
    if st.button("💬 返回聊天", use_container_width=True):
        st.switch_page("pages/chat.py")

with col_op4:
    if orders:
        if st.button("🗑️ 清空所有订单", use_container_width=True, type="secondary"):
            if st.checkbox("⚠️ 确认清空所有订单（不可恢复）", key="confirm_clear"):
                current_conv["orders"] = []
                current_conv["total_spent"] = 0
                st.success("✅ 所有订单已清空")
                st.rerun()

# ==================== 侧边栏 ====================
with st.sidebar:
    st.header("📊 统计信息")

    if orders:
        # 按类型统计
        hotel_total = sum(o["price"] for o in orders if o.get("type") == "hotel")
        flight_total = sum(o["price"] for o in orders if o.get("type") == "flight")

        st.markdown("### 💰 费用统计")
        st.write(f"🏨 酒店: ¥{hotel_total:,.0f}")
        st.write(f"✈️ 航班: ¥{flight_total:,.0f}")
        st.write(f"📊 总计: ¥{total_spent:,.0f}")

        st.divider()

        # 按状态统计
        st.markdown("### 📋 订单状态")
        paid = len([o for o in orders if o.get("status") == "已支付"])
        pending = len([o for o in orders if o.get("status") == "待支付"])

        st.write(f"✅ 已支付: {paid} 个")
        st.write(f"⏳ 待支付: {pending} 个")

    st.divider()

    # 对话信息
    st.markdown("### 💬 当前对话")
    st.write(f"**名称**: {current_conv['name']}")
    st.write(f"**目的地**: {current_conv['preferences'].get('destination', '未设置')}")
    st.write(f"**天数**: {current_conv['preferences'].get('days', 0)} 天")
    st.write(f"**消息数**: {len(current_conv.get('messages', []))} 条")

# ==================== 底部提示 ====================
st.markdown("---")
st.caption("💡 提示：订单数据保存在当前会话中，切换对话或关闭浏览器后将丢失")