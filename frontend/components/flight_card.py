"""
改进版酒店卡片组件 - 蓝绿色主题
特点：
1. 蓝绿色配色方案
2. 减少emoji使用
3. 详情向下展开
"""

import streamlit as st


def display_hotel_card_v2(hotel, key_prefix="hotel", message_id=0):
    """
    改进版酒店卡片 - 蓝绿色主题

    参数:
        hotel: 酒店数据
        key_prefix: 按钮key前缀
        message_id: 消息ID
    """

    # 蓝绿色主题CSS
    st.markdown("""
    <style>
    .hotel-card-v2 {
        background: #ffffff;
        border: 1px solid #b2dfdb;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,150,136,0.1);
    }

    .hotel-card-v2:hover {
        box-shadow: 0 4px 12px rgba(0,150,136,0.2);
        transform: translateY(-2px);
    }

    .hotel-header-v2 {
        display: flex;
        justify-content: space-between;
        align-items: start;
        margin-bottom: 16px;
    }

    .hotel-title-v2 {
        font-size: 20px;
        font-weight: 600;
        color: #004d40;
        margin: 0;
        line-height: 1.4;
    }

    .hotel-rating-v2 {
        display: inline-flex;
        align-items: center;
        background: #e0f2f1;
        color: #00695c;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 14px;
        font-weight: 600;
    }

    .hotel-location-v2 {
        color: #00897b;
        font-size: 14px;
        margin: 8px 0;
        font-weight: 500;
    }

    .hotel-amenities-v2 {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin: 12px 0;
    }

    .amenity-tag-v2 {
        background: #e0f2f1;
        color: #00695c;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
    }

    .hotel-price-section-v2 {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 16px;
        border-top: 1px solid #e0f2f1;
        margin-top: 16px;
    }

    .price-info-v2 {
        display: flex;
        flex-direction: column;
    }

    .price-amount-v2 {
        font-size: 28px;
        font-weight: 700;
        color: #00897b;
        line-height: 1;
    }

    .price-unit-v2 {
        font-size: 13px;
        color: #00897b;
        margin-top: 4px;
    }

    .hotel-details-section {
        background: #f1f8f7;
        border: 1px solid #b2dfdb;
        border-radius: 8px;
        padding: 16px;
        margin-top: 12px;
    }

    .hotel-details-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e0f2f1;
    }

    .hotel-details-row:last-child {
        border-bottom: none;
    }

    .hotel-details-label {
        color: #00897b;
        font-size: 13px;
        font-weight: 500;
    }

    .hotel-details-value {
        color: #004d40;
        font-size: 13px;
    }

    .amenities-list {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
        margin-top: 8px;
    }

    .amenity-item {
        color: #00695c;
        font-size: 13px;
        padding: 4px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    # 生成唯一的key
    hotel_id = hotel.get('id', 0)
    details_key = f"{key_prefix}_details_{message_id}_{hotel_id}"
    book_key = f"{key_prefix}_book_{message_id}_{hotel_id}"

    # 初始化详情展开状态
    if details_key not in st.session_state:
        st.session_state[details_key] = False

    with st.container():
        st.markdown("<div class='hotel-card-v2'>", unsafe_allow_html=True)

        # 顶部：标题和评分
        col_header, col_rating = st.columns([3, 1])

        with col_header:
            st.markdown(f"<h3 class='hotel-title-v2'>{hotel.get('name', 'Unknown Hotel')}</h3>",
                        unsafe_allow_html=True)

        with col_rating:
            rating = hotel.get('rating', 0)
            st.markdown(f"<div class='hotel-rating-v2'>★ {rating}</div>",
                        unsafe_allow_html=True)

        # 位置信息
        location = hotel.get('location', hotel.get('address', 'N/A'))
        st.markdown(f"""
            <div class='hotel-location-v2'>
                位置: {location}
            </div>
        """, unsafe_allow_html=True)

        # 设施标签（最多显示3个）
        amenities = hotel.get('amenities', [])
        if amenities:
            amenities_html = "<div class='hotel-amenities-v2'>"
            for amenity in amenities[:3]:
                amenities_html += f"<span class='amenity-tag-v2'>{amenity}</span>"
            if len(amenities) > 3:
                amenities_html += f"<span class='amenity-tag-v2'>+{len(amenities) - 3}项设施</span>"
            amenities_html += "</div>"
            st.markdown(amenities_html, unsafe_allow_html=True)

        # 底部：价格和操作按钮
        st.markdown("<div class='hotel-price-section-v2'>", unsafe_allow_html=True)

        col_price, col_btn1, col_btn2 = st.columns([2, 1, 1])

        with col_price:
            price = hotel.get('price', 0)
            st.markdown(f"""
                <div class='price-info-v2'>
                    <div class='price-amount-v2'>¥{price}</div>
                    <div class='price-unit-v2'>每晚</div>
                </div>
            """, unsafe_allow_html=True)

        with col_btn1:
            # 展开/收起详情按钮
            button_text = "收起详情" if st.session_state[details_key] else "查看详情"
            if st.button(button_text,
                         key=details_key + "_btn",
                         use_container_width=True):
                st.session_state[details_key] = not st.session_state[details_key]
                st.rerun()

        with col_btn2:
            if st.button("预订",
                         key=book_key,
                         type="primary",
                         use_container_width=True):
                return "book"

        st.markdown("</div>", unsafe_allow_html=True)  # price-section-v2

        # 向下展开的详情区域
        if st.session_state[details_key]:
            st.markdown("<div class='hotel-details-section'>", unsafe_allow_html=True)
            st.markdown("<h4 style='color: #00695c; margin-bottom: 12px;'>酒店详情</h4>", unsafe_allow_html=True)

            # 基本信息
            details_html = f"""
            <div class='hotel-details-row'>
                <span class='hotel-details-label'>地址</span>
                <span class='hotel-details-value'>{hotel.get('address', 'N/A')}</span>
            </div>
            <div class='hotel-details-row'>
                <span class='hotel-details-label'>联系电话</span>
                <span class='hotel-details-value'>{hotel.get('tel', 'N/A')}</span>
            </div>
            <div class='hotel-details-row'>
                <span class='hotel-details-label'>评分</span>
                <span class='hotel-details-value'>{hotel.get('rating', 'N/A')}/5.0</span>
            </div>
            """
            st.markdown(details_html, unsafe_allow_html=True)

            # 完整设施列表
            if amenities:
                st.markdown("<div class='hotel-details-row'>", unsafe_allow_html=True)
                st.markdown("<span class='hotel-details-label'>设施服务</span>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                amenities_list_html = "<div class='amenities-list'>"
                for amenity in amenities:
                    amenities_list_html += f"<div class='amenity-item'>✓ {amenity}</div>"
                amenities_list_html += "</div>"
                st.markdown(amenities_list_html, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)  # hotel-card-v2

    return None


def display_hotel_list_v2(hotels, message_id=0):
    """
    改进版酒店列表展示

    参数:
        hotels: 酒店列表
        message_id: 消息ID
    """
    if not hotels:
        st.info("未找到符合条件的酒店")
        return

    # 筛选器（简洁版）
    with st.expander("筛选条件", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            max_price = st.number_input(
                "最高价格（元/晚）",
                min_value=0,
                max_value=10000,
                value=5000,
                step=100,
                key=f"hotel_filter_price_{message_id}"
            )

        with col2:
            min_rating = st.slider(
                "最低评分",
                min_value=0.0,
                max_value=5.0,
                value=3.0,
                step=0.5,
                key=f"hotel_filter_rating_{message_id}"
            )

    # 筛选酒店
    filtered_hotels = [
        h for h in hotels
        if h.get('price', 0) <= max_price and h.get('rating', 0) >= min_rating
    ]

    # 显示结果统计
    st.markdown(f"""
        <div style='background: #e0f2f1; padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; border: 1px solid #b2dfdb;'>
            <span style='color: #00695c; font-size: 14px;'>
                找到 <strong style='color: #004d40;'>{len(filtered_hotels)}</strong> 家符合条件的酒店
            </span>
        </div>
    """, unsafe_allow_html=True)

    # 显示酒店卡片
    for hotel in filtered_hotels[:10]:  # 限制显示前10个
        display_hotel_card_v2(hotel, key_prefix="hotel", message_id=message_id)