"""
现代化酒店卡片组件 - 统一预算版
新功能：
1. ⭐ 根据评分显示星星
2. 💰 统一预算检查
3. ✅ 预订成功弹窗
4. 简洁的设计
"""

import streamlit as st


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
    """获取剩余预算 - 与chat.py保持一致"""
    if "current_trip" in st.session_state and "total_spent" in st.session_state:
        total_budget = st.session_state.current_trip.get("budget", 5000)
        return total_budget - st.session_state.total_spent
    return 0


def display_hotel_card_v2(hotel, key_prefix="hotel", message_id=0, on_book_callback=None):
    """
    现代化酒店卡片展示 - 带统一预算检查

    参数:
        hotel: 酒店数据字典
        key_prefix: 按钮key前缀
        message_id: 消息ID
        on_book_callback: 预订回调函数
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
    </style>
    """, unsafe_allow_html=True)

    hotel_id = hotel.get('id', 0)
    details_key = f"{key_prefix}_detail_{message_id}_{hotel_id}"
    book_key = f"{key_prefix}_book_{message_id}_{hotel_id}"

    if details_key not in st.session_state:
        st.session_state[details_key] = False

    # ✅ 获取价格和剩余预算
    price = hotel.get('price', 0)
    remaining_budget = get_remaining_budget()
    can_afford = price <= remaining_budget

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
                <div class='hotel-price-modern'>¥{price:,}</div>
                <div class='hotel-price-unit'>每晚</div>
            </div>
        """, unsafe_allow_html=True)

    # ✅ 预算提示
    if not can_afford:
        st.markdown(f"""
            <div class='budget-warning-inline'>
                💰 预算不足<br>
                需要: ¥{price:,} | 剩余: ¥{remaining_budget:,}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class='budget-ok-inline'>
                ✅ 预算充足 | 剩余: ¥{remaining_budget:,}
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)

    col_btn1, col_btn2, col_space = st.columns([1, 1, 2])

    with col_btn1:
        button_text = "收起详情" if st.session_state[details_key] else "查看详情"
        if st.button(
            button_text,
            key=details_key + "_btn",
            use_container_width=True
        ):
            st.session_state[details_key] = not st.session_state[details_key]
            st.rerun()

    with col_btn2:
        # ✅ 根据预算状态决定按钮
        if can_afford:
            if st.button(
                "预订",
                key=book_key,
                type="primary",
                use_container_width=True
            ):
                if on_book_callback:
                    on_book_callback(hotel, price)
                    st.rerun()
                else:
                    # 默认行为
                    st.session_state.total_spent = st.session_state.get("total_spent", 0) + price
                    st.success(f"✅ 已预订! 花费 ¥{price:,}")
                    st.balloons()
                    st.rerun()
        else:
            st.button(
                "预算不足",
                key=book_key,
                disabled=True,
                use_container_width=True
            )

    # 详情区域
    if st.session_state[details_key]:
        st.markdown("""
        <div style='background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; 
                    padding: 16px; margin-top: 12px;'>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                    border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
            <span style='color: #6b7280; font-weight: 500;'>完整地址</span>
            <span style='color: #111827; font-weight: 600;'>{hotel.get('address', 'N/A')}</span>
        </div>
        <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                    border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
            <span style='color: #6b7280; font-weight: 500;'>联系电话</span>
            <span style='color: #111827; font-weight: 600;'>{hotel.get('tel', 'N/A')}</span>
        </div>
        <div style='display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px;'>
            <span style='color: #6b7280; font-weight: 500;'>评分</span>
            <span style='color: #111827; font-weight: 600;'>{stars_html}</span>
        </div>
        """, unsafe_allow_html=True)

        if amenities:
            st.markdown("<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;'>",
                       unsafe_allow_html=True)
            st.markdown("<span style='color: #6b7280; font-weight: 500;'>所有设施服务</span>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)

            cols = st.columns(2)
            for i, amenity in enumerate(amenities):
                with cols[i % 2]:
                    st.markdown(f"<div style='color: #374151; font-size: 13px; padding: 2px 0;'>• {amenity}</div>",
                               unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    return None


def display_hotel_list_v2(hotels, message_id=0, on_book_callback=None):
    """
    现代化酒店列表展示 - 带统一预算管理

    参数:
        hotels: 酒店列表
        message_id: 消息ID
        on_book_callback: 预订回调函数
    """
    if not hotels:
        st.info("未找到符合条件的酒店")
        return

    # ✅ 显示剩余预算
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
    with st.expander("筛选条件", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            max_price = st.number_input(
                "最高价格(元/晚)",
                min_value=0,
                max_value=10000,
                value=min(5000, int(remaining_budget)) if remaining_budget > 0 else 5000,
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

    # ✅ 按价格排序,便宜的在前
    filtered.sort(key=lambda x: x.get('price', 0))

    # 显示酒店卡片
    for hotel in filtered[:10]:
        display_hotel_card_v2(
            hotel,
            key_prefix="hotel",
            message_id=message_id,
            on_book_callback=on_book_callback
        )


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="现代化酒店卡片 - 统一预算版", layout="wide")

    st.title("现代化酒店卡片组件 - 统一预算版")
    st.caption("演示统一预算管理和预订功能")

    # 模拟预算状态
    if "total_spent" not in st.session_state:
        st.session_state.total_spent = 0

    if "current_trip" not in st.session_state:
        st.session_state.current_trip = {"budget": 5000}

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
            'price': 1280,
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
            'name': '经济型酒店',
            'location': '虹桥机场',
            'address': '闵行区虹桥路888号',
            'tel': '021-87654321',
            'rating': 3.5,
            'price': 188,
            'amenities': ['免费WiFi']
        },
    ]

    def test_booking_callback(hotel, price):
        """测试预订回调"""
        st.session_state.total_spent += price
        st.success(f"""
        ✅ 预订成功!
        
        - 酒店: {hotel['name']}
        - 价格: ¥{price:,}
        - 剩余预算: ¥{get_remaining_budget():,}
        """)
        st.balloons()

    display_hotel_list_v2(test_hotels, message_id=0, on_book_callback=test_booking_callback)