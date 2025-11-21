"""
现代化酒店卡片组件 - ChatGPT风格
特点：
1. 简洁的设计
2. 适量使用浅绿色
3. 无过度emoji
4. 流畅的交互
"""

import streamlit as st


def display_hotel_card_v2(hotel, key_prefix="hotel", message_id=0):
    """
    现代化酒店卡片展示

    参数:
        hotel: 酒店数据字典
        key_prefix: 按钮key前缀
        message_id: 消息ID（避免key冲突）
    """

    # 现代化CSS样式
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
        color: #059669;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        margin-right: 8px;
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
    
    .hotel-details-box {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 16px;
        margin-top: 12px;
    }
    
    .detail-row {
        display: flex;
        justify-content: space-between;
        padding: 8px 0;
        border-bottom: 1px solid #e5e7eb;
        font-size: 14px;
    }
    
    .detail-row:last-child {
        border-bottom: none;
    }
    
    .detail-label {
        color: #6b7280;
        font-weight: 500;
    }
    
    .detail-value {
        color: #111827;
        font-weight: 600;
    }
    </style>
    """, unsafe_allow_html=True)

    # 生成唯一key
    hotel_id = hotel.get('id', 0)
    details_key = f"{key_prefix}_detail_{message_id}_{hotel_id}"
    book_key = f"{key_prefix}_book_{message_id}_{hotel_id}"

    # 初始化展开状态
    if details_key not in st.session_state:
        st.session_state[details_key] = False

    # 开始渲染卡片
    st.markdown("<div class='modern-hotel-card'>", unsafe_allow_html=True)

    # 顶部：名称和评分
    col_info, col_price = st.columns([3, 1])

    with col_info:
        # 酒店名称
        st.markdown(
            f"<div class='hotel-name-modern'>{hotel.get('name', 'Unknown Hotel')}</div>",
            unsafe_allow_html=True
        )

        # 位置
        location = hotel.get('location', hotel.get('address', 'N/A'))
        st.markdown(
            f"<div class='hotel-location-modern'>{location}</div>",
            unsafe_allow_html=True
        )

        # 评分和设施
        rating = hotel.get('rating', 0)
        st.markdown(
            f"<span class='hotel-rating-badge'>评分 {rating}/5.0</span>",
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
        # 价格
        price = hotel.get('price', 0)
        st.markdown(f"""
            <div style='text-align: right;'>
                <div class='hotel-price-modern'>¥{price}</div>
                <div class='hotel-price-unit'>每晚</div>
            </div>
        """, unsafe_allow_html=True)

    # 底部：操作按钮
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
        if st.button(
            "预订",
            key=book_key,
            type="primary",
            use_container_width=True
        ):
            st.success("已添加到订单")
            return "book"

    # 详情区域（展开）
    if st.session_state[details_key]:
        st.markdown("<div class='hotel-details-box'>", unsafe_allow_html=True)

        # 基本信息
        st.markdown(f"""
        <div class='detail-row'>
            <span class='detail-label'>完整地址</span>
            <span class='detail-value'>{hotel.get('address', 'N/A')}</span>
        </div>
        <div class='detail-row'>
            <span class='detail-label'>联系电话</span>
            <span class='detail-value'>{hotel.get('tel', 'N/A')}</span>
        </div>
        <div class='detail-row'>
            <span class='detail-label'>评分</span>
            <span class='detail-value'>{hotel.get('rating', 'N/A')}/5.0</span>
        </div>
        """, unsafe_allow_html=True)

        # 完整设施列表
        if amenities:
            st.markdown("<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;'>",
                       unsafe_allow_html=True)
            st.markdown("<span class='detail-label'>所有设施服务</span>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)

            # 分列显示所有设施
            cols = st.columns(2)
            for i, amenity in enumerate(amenities):
                with cols[i % 2]:
                    st.markdown(f"<div style='color: #374151; font-size: 13px; padding: 2px 0;'>• {amenity}</div>",
                               unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    return None


def display_hotel_list_v2(hotels, message_id=0):
    """
    现代化酒店列表展示

    参数:
        hotels: 酒店列表
        message_id: 消息ID
    """
    if not hotels:
        st.info("未找到符合条件的酒店")
        return

    # 结果统计
    st.markdown(f"""
    <div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; 
                padding: 12px 16px; margin-bottom: 16px;'>
        <span style='color: #166534; font-size: 14px;'>
            找到 <strong>{len(hotels)}</strong> 家酒店
        </span>
    </div>
    """, unsafe_allow_html=True)

    # 简洁筛选器
    with st.expander("筛选条件", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            max_price = st.number_input(
                "最高价格（元/晚）",
                min_value=0,
                max_value=10000,
                value=5000,
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

    # 筛选和显示
    filtered = [
        h for h in hotels
        if h.get('price', 0) <= max_price and h.get('rating', 0) >= min_rating
    ]

    if not filtered:
        st.warning("没有符合筛选条件的酒店")
        return

    # 显示酒店卡片
    for hotel in filtered[:10]:
        display_hotel_card_v2(hotel, key_prefix="hotel", message_id=message_id)


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="现代化酒店卡片", layout="wide")

    st.title("现代化酒店卡片组件")
    st.caption("ChatGPT风格设计")

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
        }
    ]

    display_hotel_list_v2(test_hotels, message_id=0)