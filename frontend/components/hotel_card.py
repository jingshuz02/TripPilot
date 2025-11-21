"""
现代化酒店卡片组件 - 简洁折叠版
功能：
1. ⭐ 根据评分显示星星
2. 💰 统一预算检查
3. 📅 入住/离店日期选择（自动计算晚数）
4. 🎯 只有第一个酒店默认展开
5. ✅ 预订按钮在展开区域内
"""

import streamlit as st
from datetime import datetime, timedelta


def render_star_rating(rating):
    """根据评分渲染星星"""
    full_stars = int(rating)
    has_half = (rating - full_stars) >= 0.5
    empty_stars = 5 - full_stars - (1 if has_half else 0)

    stars_html = ""
    for _ in range(full_stars):
        stars_html += "⭐"
    if has_half:
        stars_html += "✨"
    for _ in range(empty_stars):
        stars_html += "☆"

    return f"""
    <div style='display: inline-flex; align-items: center;'>
        <span style='font-size: 16px; letter-spacing: 2px;'>{stars_html}</span>
        <span style='margin-left: 8px; color: #059669; font-weight: 600; font-size: 14px;'>
            {rating:.1f}
        </span>
    </div>
    """


def get_remaining_budget():
    """获取剩余预算"""
    if "current_trip" in st.session_state and "total_spent" in st.session_state:
        total_budget = st.session_state.current_trip.get("budget", 5000)
        return total_budget - st.session_state.total_spent
    return 0


def display_hotel_card_v2(hotel, key_prefix="hotel", message_id=0, on_book_callback=None, is_first=False):
    """
    现代化酒店卡片展示 - 简洁折叠版

    参数:
        hotel: 酒店数据字典
        key_prefix: 按钮key前缀
        message_id: 消息ID
        on_book_callback: 预订回调函数
        is_first: 是否是第一个酒店（默认展开）
    """

    st.markdown("""
    <style>
    .modern-hotel-card {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
    }
    
    .modern-hotel-card:hover {
        border-color: #10b981;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    
    .hotel-name-modern {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 8px;
        line-height: 1.4;
    }
    
    .hotel-location-modern {
        color: #6b7280;
        font-size: 14px;
        margin-bottom: 12px;
    }
    
    .hotel-rating-badge {
        display: inline-flex;
        align-items: center;
        background: #f0fdf4;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    
    .amenity-tag-modern {
        display: inline-block;
        background: #f9fafb;
        color: #374151;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 12px;
        margin-right: 6px;
        margin-bottom: 6px;
        border: 1px solid #e5e7eb;
    }
    
    .hotel-price-modern {
        font-size: 24px;
        font-weight: 700;
        color: #10b981;
        line-height: 1;
    }
    
    .hotel-price-unit {
        color: #6b7280;
        font-size: 13px;
        margin-top: 4px;
    }
    
    .budget-warning-inline {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #92400e;
        margin-top: 8px;
    }
    
    .budget-ok-inline {
        background: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #065f46;
        margin-top: 8px;
    }
    
    .booking-section {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-top: 16px;
    }
    
    .section-title {
        font-weight: 600;
        color: #374151;
        margin-bottom: 12px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

    hotel_id = hotel.get('id', 0)
    checkin_key = f"{key_prefix}_checkin_{message_id}_{hotel_id}"
    checkout_key = f"{key_prefix}_checkout_{message_id}_{hotel_id}"
    book_key = f"{key_prefix}_book_{message_id}_{hotel_id}"

    # ✅ 初始化日期
    if checkin_key not in st.session_state:
        if "current_trip" in st.session_state:
            start_date = st.session_state.current_trip.get("start_date")
            if start_date:
                st.session_state[checkin_key] = start_date
            else:
                st.session_state[checkin_key] = datetime.now().date()
        else:
            st.session_state[checkin_key] = datetime.now().date()

    if checkout_key not in st.session_state:
        if "current_trip" in st.session_state:
            end_date = st.session_state.current_trip.get("end_date")
            if end_date:
                st.session_state[checkout_key] = end_date
            else:
                st.session_state[checkout_key] = st.session_state[checkin_key] + timedelta(days=2)
        else:
            st.session_state[checkout_key] = st.session_state[checkin_key] + timedelta(days=2)

    price_per_night = hotel.get('price', 0)
    remaining_budget = get_remaining_budget()

    # === 酒店基本信息（始终显示）===
    st.markdown("<div class='modern-hotel-card'>", unsafe_allow_html=True)

    col_info, col_price = st.columns([3, 1])

    with col_info:
        st.markdown(
            f"<div class='hotel-name-modern'>{hotel.get('name', 'Unknown Hotel')}</div>",
            unsafe_allow_html=True
        )

        location = hotel.get('location', hotel.get('address', 'N/A'))
        st.markdown(
            f"<div class='hotel-location-modern'>📍 {location}</div>",
            unsafe_allow_html=True
        )

        rating = hotel.get('rating', 0)
        stars_html = render_star_rating(rating)
        st.markdown(
            f"<div class='hotel-rating-badge'>{stars_html}</div>",
            unsafe_allow_html=True
        )

        amenities = hotel.get('amenities', [])
        if amenities:
            amenities_html = ""
            for amenity in amenities[:3]:
                amenities_html += f"<span class='amenity-tag-modern'>{amenity}</span>"
            if len(amenities) > 3:
                amenities_html += f"<span class='amenity-tag-modern'>+{len(amenities)-3}项</span>"
            st.markdown(amenities_html, unsafe_allow_html=True)

    with col_price:
        st.markdown(f"""
            <div style='text-align: right;'>
                <div class='hotel-price-modern'>¥{price_per_night:,}</div>
                <div class='hotel-price-unit'>每晚</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # === 展开区域（详情 + 预订） ===
    with st.expander("📋 查看详情并预订", expanded=is_first):

        # 酒店详细信息
        st.markdown("<div style='margin-bottom: 16px;'>", unsafe_allow_html=True)

        col_detail1, col_detail2 = st.columns(2)

        with col_detail1:
            st.write(f"**完整地址**: {hotel.get('address', 'N/A')}")
            st.write(f"**联系电话**: {hotel.get('tel', 'N/A')}")

        with col_detail2:
            st.write(f"**评分**: {rating:.1f}/5.0")
            st.write(f"**价格**: ¥{price_per_night:,}/晚")

        if amenities:
            st.markdown("<div style='margin-top: 12px;'>", unsafe_allow_html=True)
            st.write("**所有设施服务**:")
            cols = st.columns(2)
            for i, amenity in enumerate(amenities):
                with cols[i % 2]:
                    st.caption(f"• {amenity}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

        # === 预订区域 ===
        st.markdown("<div class='booking-section'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📅 选择入住日期</div>", unsafe_allow_html=True)

        col_date1, col_date2 = st.columns(2)

        with col_date1:
            checkin_date = st.date_input(
                "入住日期",
                value=st.session_state[checkin_key],
                min_value=datetime.now().date(),
                key=f"{checkin_key}_widget"
            )
            st.session_state[checkin_key] = checkin_date

        with col_date2:
            checkout_date = st.date_input(
                "离店日期",
                value=st.session_state[checkout_key],
                min_value=checkin_date + timedelta(days=1),
                key=f"{checkout_key}_widget"
            )
            st.session_state[checkout_key] = checkout_date

        # ✅ 计算晚数
        nights = (checkout_date - checkin_date).days
        if nights < 1:
            nights = 1
            st.warning("⚠️ 离店日期必须晚于入住日期")

        # ✅ 计算总价
        total_price = price_per_night * nights

        # 显示计算结果
        st.markdown(f"""
        <div style='background: white; border: 1px solid #e5e7eb; border-radius: 8px; 
                    padding: 12px; margin-top: 16px; margin-bottom: 16px;'>
            <div style='text-align: center;'>
                <div style='color: #6b7280; font-size: 13px; margin-bottom: 4px;'>
                    {checkin_date.strftime('%Y年%m月%d日')} - {checkout_date.strftime('%Y年%m月%d日')}
                </div>
                <div style='color: #10b981; font-size: 20px; font-weight: 700;'>
                    共 {nights} 晚 × ¥{price_per_night:,}/晚 = ¥{total_price:,}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ✅ 预算检查
        can_afford = total_price <= remaining_budget

        if not can_afford:
            st.markdown(f"""
                <div class='budget-warning-inline'>
                    ⚠️ 预算不足 | 需要: ¥{total_price:,} | 剩余: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='budget-ok-inline'>
                    ✅ 预算充足 | 剩余预算: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # === 预订按钮 ===
        st.markdown("<div style='margin-top: 16px;'>", unsafe_allow_html=True)

        if can_afford:
            if st.button(
                f"✅ 预订 {nights}晚 - 总价 ¥{total_price:,}",
                key=book_key,
                type="primary",
                use_container_width=True
            ):
                if on_book_callback:
                    # 准备完整的预订数据
                    hotel_with_booking = hotel.copy()
                    hotel_with_booking['nights'] = nights
                    hotel_with_booking['total_price'] = total_price
                    hotel_with_booking['checkin_date'] = checkin_date
                    hotel_with_booking['checkout_date'] = checkout_date

                    on_book_callback(hotel_with_booking, total_price)
                else:
                    # 默认行为
                    st.session_state.total_spent = st.session_state.get("total_spent", 0) + total_price
                    st.success(f"""
                    ✅ 预订成功！
                    
                    - 酒店: {hotel.get('name')}
                    - 入住: {checkin_date.strftime('%Y年%m月%d日')}
                    - 离店: {checkout_date.strftime('%Y年%m月%d日')}
                    - 晚数: {nights}晚
                    - 总价: ¥{total_price:,}
                    """)
                    st.balloons()
                    st.rerun()
        else:
            st.button(
                "❌ 预算不足，无法预订",
                key=book_key,
                disabled=True,
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)


def display_hotel_list_v2(hotels, message_id=0, on_book_callback=None):
    """
    现代化酒店列表展示

    参数:
        hotels: 酒店列表
        message_id: 消息ID
        on_book_callback: 预订回调函数
    """
    if not hotels:
        st.info("未找到符合条件的酒店")
        return

    remaining_budget = get_remaining_budget()

    col_result, col_budget = st.columns([2, 1])
    with col_result:
        st.markdown(f"""
        <div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; 
                    padding: 12px 16px; margin-bottom: 16px;'>
            <span style='color: #166534; font-size: 14px;'>
                找到 <strong>{len(hotels)}</strong> 家酒店
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_budget:
        st.metric("💰 剩余预算", f"¥{remaining_budget:,}")

    # 简洁筛选器
    with st.expander("🔧 筛选条件", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            default_max = min(1000, int(remaining_budget * 0.4)) if remaining_budget > 0 else 1000
            max_price = st.number_input(
                "最高价格(元/晚)",
                min_value=0,
                max_value=10000,
                value=default_max,
                step=100,
                key=f"hotel_price_{message_id}"
            )

        with col2:
            min_rating = st.slider(
                "最低评分",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
                key=f"hotel_rating_{message_id}"
            )

    # 筛选
    filtered = [
        h for h in hotels
        if h.get('price', 0) <= max_price and h.get('rating', 0) >= min_rating
    ]

    if not filtered:
        st.warning("没有符合筛选条件的酒店")
        return

    # 按价格排序
    filtered.sort(key=lambda x: x.get('price', 0))

    # ✅ 显示酒店卡片（只有第一个展开）
    for idx, hotel in enumerate(filtered[:10]):
        display_hotel_card_v2(
            hotel,
            key_prefix="hotel",
            message_id=message_id,
            on_book_callback=on_book_callback,
            is_first=(idx == 0)  # 只有第一个酒店默认展开
        )


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="酒店卡片 - 简洁折叠版", layout="wide")

    st.title("🏨 酒店卡片组件 - 简洁折叠版")
    st.caption("只有第一个酒店默认展开，预订功能在展开区域内")

    # 模拟预算状态
    if "total_spent" not in st.session_state:
        st.session_state.total_spent = 0

    if "current_trip" not in st.session_state:
        st.session_state.current_trip = {
            "budget": 5000,
            "start_date": datetime.now().date(),
            "end_date": datetime.now().date() + timedelta(days=3)
        }

    # 侧边栏显示预算
    with st.sidebar:
        st.header("💰 预算管理")
        total_budget = st.session_state.current_trip["budget"]
        remaining = total_budget - st.session_state.total_spent

        st.metric("总预算", f"¥{total_budget:,}")
        st.metric("剩余", f"¥{remaining:,}", delta=f"-¥{st.session_state.total_spent:,}")
        st.progress(min(st.session_state.total_spent / total_budget, 1.0))

    test_hotels = [
        {
            'id': 1,
            'name': '上海浦东香格里拉大酒店',
            'location': '浦东新区',
            'address': '浦东新区富城路33号',
            'tel': '021-68828888',
            'rating': 4.8,
            'price': 680,
            'amenities': ['免费WiFi', '健身房', '游泳池', '商务中心', '停车场', '早餐']
        },
        {
            'id': 2,
            'name': '如家快捷酒店',
            'location': '人民广场',
            'address': '黄浦区南京东路123号',
            'tel': '021-12345678',
            'rating': 4.2,
            'price': 299,
            'amenities': ['免费WiFi', '24小时前台']
        },
        {
            'id': 3,
            'name': '汉庭酒店',
            'location': '虹桥机场',
            'address': '闵行区虹桥路888号',
            'tel': '021-87654321',
            'rating': 3.9,
            'price': 188,
            'amenities': ['免费WiFi', '自助早餐']
        },
    ]

    def test_booking_callback(hotel, price):
        """测试预订回调"""
        st.session_state.total_spent += price
        nights = hotel.get('nights', 1)
        checkin = hotel.get('checkin_date')
        checkout = hotel.get('checkout_date')

        st.success(f"""
        ✅ 预订成功!
        
        - 酒店: {hotel['name']}
        - 入住: {checkin.strftime('%Y年%m月%d日')}
        - 离店: {checkout.strftime('%Y年%m月%d日')}
        - 晚数: {nights}晚
        - 总价: ¥{price:,}
        - 剩余预算: ¥{get_remaining_budget():,}
        """)
        st.balloons()

    display_hotel_list_v2(test_hotels, message_id=0, on_book_callback=test_booking_callback)