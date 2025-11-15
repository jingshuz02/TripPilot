import streamlit as st

def display_hotel_card(hotel, key_prefix="hotel"):
    """
    显示酒店卡片（优化版）
    """
    with st.container(border=True):
        # 自定义CSS
        st.markdown("""
        <style>
        .hotel-card {
            transition: transform 0.2s;
        }
        .hotel-card:hover {
            transform: translateY(-2px);
        }
        .hotel-name {
            color: #2c3e50;
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .hotel-rating {
            color: #f39c12;
            font-size: 16px;
        }
        .hotel-price {
            color: #27ae60;
            font-size: 28px;
            font-weight: bold;
        }
        .hotel-total {
            color: #7f8c8d;
            font-size: 14px;
        }
        .amenity-badge {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 4px 10px;
            border-radius: 15px;
            font-size: 12px;
            margin: 2px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # 酒店图片占位
            st.markdown("""
            <div style='width:100%; height:180px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            border-radius:12px; display:flex; align-items:center; 
            justify-content:center; color:white; font-size:48px;'>
            🏨
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            # 酒店名称
            st.markdown(f"<div class='hotel-name'>{hotel.get('name', 'N/A')}</div>", 
                       unsafe_allow_html=True)
            
            # 评分和位置
            rating = hotel.get('rating', 0)
            stars = "⭐" * int(rating)
            st.markdown(f"<div class='hotel-rating'>{stars} {rating}/5.0 · 📍 {hotel.get('location', 'N/A')}</div>", 
                       unsafe_allow_html=True)
            
            st.write("")  # 间距
            
            # 描述
            st.write(hotel.get('desc', ''))
            
            # 设施标签
            amenities = hotel.get('amenities', [])
            if amenities:
                amenity_html = "".join([f"<span class='amenity-badge'>{a}</span>" for a in amenities])
                st.markdown(amenity_html, unsafe_allow_html=True)
        
        st.divider()
        
        # 底部：价格和按钮
        col_a, col_b, col_c = st.columns([2, 2, 1])
        
        with col_a:
            st.markdown(f"<div class='hotel-price'>${hotel.get('price', 0)}</div>", 
                       unsafe_allow_html=True)
            st.markdown(f"<div class='hotel-total'>每晚 · 共{hotel.get('nights', 1)}晚 = ${hotel.get('total_price', 0)}</div>", 
                       unsafe_allow_html=True)
        
        with col_b:
            if hotel.get('desc'):
                with st.expander("📖 查看更多详情"):
                    st.write(hotel['desc'])
                    st.write(f"**入住时间**: 14:00")
                    st.write(f"**退房时间**: 12:00")
                    st.write(f"**取消政策**: 入住前24小时免费取消")
        
        with col_c:
            if st.button("💳 预订", key=f"{key_prefix}_book_{hotel.get('id')}", 
                        type="primary", use_container_width=True):
                return "book"
    
    return None


def display_hotel_filters():
    """显示酒店筛选器（紧凑版）"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        price_range = st.slider(
            "💰 价格范围 (USD/晚)",
            min_value=0,
            max_value=500,
            value=(0, 300),
            step=20,
            key="filter_price"
        )
    
    with col2:
        min_rating = st.select_slider(
            "⭐ 最低评分",
            options=[3.0, 3.5, 4.0, 4.5, 5.0],
            value=3.0,
            key="filter_rating"
        )
    
    with col3:
        amenities_filter = st.multiselect(
            "🏨 设施要求",
            ["免费WiFi", "早餐", "停车场", "健身房", "游泳池"],
            default=[],
            key="filter_amenities"
        )
    
    return {
        "price_range": price_range,
        "min_rating": min_rating,
        "amenities": amenities_filter
    }