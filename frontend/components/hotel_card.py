"""
Modern Hotel Card Component - Compact Collapsible Version
Features:
1. ⭐ Display stars based on rating
2. 💰 Unified budget check
3. 📅 Check-in/check-out date selection (automatically calculates nights)
4. 🎯 Only the first hotel is expanded by default
5. ✅ Booking button within expanded area
"""

import streamlit as st
from datetime import datetime, timedelta


def render_star_rating(rating):
    """Render stars based on rating"""
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
    """Get remaining budget"""
    if "current_trip" in st.session_state and "total_spent" in st.session_state:
        total_budget = st.session_state.current_trip.get("budget", 5000)
        return total_budget - st.session_state.total_spent
    return 0


def display_hotel_card_v2(hotel, key_prefix="hotel", message_id=0, on_book_callback=None, is_first=False):
    """
    Modern hotel card display - compact collapsible version

    Parameters:
        hotel: Hotel data dictionary
        key_prefix: Prefix for button keys
        message_id: Message ID
        on_book_callback: Booking callback function
        is_first: Whether it's the first hotel (expanded by default)
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

    # ✅ Initialize dates
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

    # === Hotel basic information (always displayed) ===
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
                amenities_html += f"<span class='amenity-tag-modern'>+{len(amenities)-3} more</span>"
            st.markdown(amenities_html, unsafe_allow_html=True)

    with col_price:
        st.markdown(f"""
            <div style='text-align: right;'>
                <div class='hotel-price-modern'>¥{price_per_night:,}</div>
                <div class='hotel-price-unit'>per night</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # === Expanded area (details + booking) ===
    with st.expander("📋 View details and book", expanded=is_first):

        # Hotel details
        st.markdown("<div style='margin-bottom: 16px;'>", unsafe_allow_html=True)

        col_detail1, col_detail2 = st.columns(2)

        with col_detail1:
            st.write(f"**Full address**: {hotel.get('address', 'N/A')}")
            st.write(f"**Contact phone**: {hotel.get('tel', 'N/A')}")

        with col_detail2:
            st.write(f"**Rating**: {rating:.1f}/5.0")
            st.write(f"**Price**: ¥{price_per_night:,}/night")

        if amenities:
            st.markdown("<div style='margin-top: 12px;'>", unsafe_allow_html=True)
            st.write("**All amenities and services**:")
            cols = st.columns(2)
            for i, amenity in enumerate(amenities):
                with cols[i % 2]:
                    st.caption(f"• {amenity}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()

        # === Booking section ===
        st.markdown("<div class='booking-section'>", unsafe_allow_html=True)
        st.markdown("<div class='section-title'>📅 Select check-in dates</div>", unsafe_allow_html=True)

        col_date1, col_date2 = st.columns(2)

        with col_date1:
            checkin_date = st.date_input(
                "Check-in date",
                value=st.session_state[checkin_key],
                min_value=datetime.now().date(),
                key=f"{checkin_key}_widget"
            )
            st.session_state[checkin_key] = checkin_date

        with col_date2:
            checkout_date = st.date_input(
                "Check-out date",
                value=st.session_state[checkout_key],
                min_value=checkin_date + timedelta(days=1),
                key=f"{checkout_key}_widget"
            )
            st.session_state[checkout_key] = checkout_date

        # ✅ Calculate number of nights
        nights = (checkout_date - checkin_date).days
        if nights < 1:
            nights = 1
            st.warning("⚠️ Check-out date must be after check-in date")

        # ✅ Calculate total price
        total_price = price_per_night * nights

        # Display calculation result
        st.markdown(f"""
        <div style='background: white; border: 1px solid #e5e7eb; border-radius: 8px; 
                    padding: 12px; margin-top: 16px; margin-bottom: 16px;'>
            <div style='text-align: center;'>
                <div style='color: #6b7280; font-size: 13px; margin-bottom: 4px;'>
                    {checkin_date.strftime('%Y-%m-%d')} - {checkout_date.strftime('%Y-%m-%d')}
                </div>
                <div style='color: #10b981; font-size: 20px; font-weight: 700;'>
                    Total {nights} night(s) × ¥{price_per_night:,}/night = ¥{total_price:,}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ✅ Budget check
        can_afford = total_price <= remaining_budget

        if not can_afford:
            st.markdown(f"""
                <div class='budget-warning-inline'>
                    ⚠️ Insufficient budget | Required: ¥{total_price:,} | Remaining: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='budget-ok-inline'>
                    ✅ Budget sufficient | Remaining budget: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # === Booking button ===
        st.markdown("<div style='margin-top: 16px;'>", unsafe_allow_html=True)

        if can_afford:
            if st.button(
                f"✅ Book {nights} night(s) - Total ¥{total_price:,}",
                key=book_key,
                type="primary",
                use_container_width=True
            ):
                if on_book_callback:
                    # Prepare complete booking data
                    hotel_with_booking = hotel.copy()
                    hotel_with_booking['nights'] = nights
                    hotel_with_booking['total_price'] = total_price
                    hotel_with_booking['checkin_date'] = checkin_date
                    hotel_with_booking['checkout_date'] = checkout_date

                    on_book_callback(hotel_with_booking, total_price)
                else:
                    # Default behavior
                    st.session_state.total_spent = st.session_state.get("total_spent", 0) + total_price
                    st.success(f"""
                    ✅ Booking successful!
                    
                    - Hotel: {hotel.get('name')}
                    - Check-in: {checkin_date.strftime('%Y-%m-%d')}
                    - Check-out: {checkout_date.strftime('%Y-%m-%d')}
                    - Nights: {nights}
                    - Total price: ¥{total_price:,}
                    """)
                    st.balloons()
                    st.rerun()
        else:
            st.button(
                "❌ Insufficient budget, cannot book",
                key=book_key,
                disabled=True,
                use_container_width=True
            )

        st.markdown("</div>", unsafe_allow_html=True)


def display_hotel_list_v2(hotels, message_id=0, on_book_callback=None):
    """
    Modern hotel list display

    Parameters:
        hotels: List of hotels
        message_id: Message ID
        on_book_callback: Booking callback function
    """
    if not hotels:
        st.info("No hotels found matching the criteria")
        return

    remaining_budget = get_remaining_budget()

    col_result, col_budget = st.columns([2, 1])
    with col_result:
        st.markdown(f"""
        <div style='background: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; 
                    padding: 12px 16px; margin-bottom: 16px;'>
            <span style='color: #166534; font-size: 14px;'>
                Found <strong>{len(hotels)}</strong> hotels
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_budget:
        st.metric("💰 Remaining budget", f"¥{remaining_budget:,}")

    # Compact filter
    with st.expander("🔧 Filter criteria", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            default_max = min(1000, int(remaining_budget * 0.4)) if remaining_budget > 0 else 1000
            max_price = st.number_input(
                "Maximum price (yuan/night)",
                min_value=0,
                max_value=10000,
                value=default_max,
                step=100,
                key=f"hotel_price_{message_id}"
            )

        with col2:
            min_rating = st.slider(
                "Minimum rating",
                min_value=0.0,
                max_value=5.0,
                value=0.0,
                step=0.5,
                key=f"hotel_rating_{message_id}"
            )

    # Filter
    filtered = [
        h for h in hotels
        if h.get('price', 0) <= max_price and h.get('rating', 0) >= min_rating
    ]

    if not filtered:
        st.warning("No hotels match the filter criteria")
        return

    # Sort by price
    filtered.sort(key=lambda x: x.get('price', 0))

    # ✅ Display hotel cards (only first one expanded)
    for idx, hotel in enumerate(filtered[:10]):
        display_hotel_card_v2(
            hotel,
            key_prefix="hotel",
            message_id=message_id,
            on_book_callback=on_book_callback,
            is_first=(idx == 0)  # Only first hotel is expanded by default
        )


# Test code
if __name__ == "__main__":
    st.set_page_config(page_title="Hotel Card - Compact Collapsible Version", layout="wide")

    st.title("🏨 Hotel Card Component - Compact Collapsible Version")
    st.caption("Only the first hotel is expanded by default, booking function is in the expanded area")

    # Simulate budget state
    if "total_spent" not in st.session_state:
        st.session_state.total_spent = 0

    if "current_trip" not in st.session_state:
        st.session_state.current_trip = {
            "budget": 5000,
            "start_date": datetime.now().date(),
            "end_date": datetime.now().date() + timedelta(days=3)
        }

    # Display budget in sidebar
    with st.sidebar:
        st.header("💰 Budget Management")
        total_budget = st.session_state.current_trip["budget"]
        remaining = total_budget - st.session_state.total_spent

        st.metric("Total budget", f"¥{total_budget:,}")
        st.metric("Remaining", f"¥{remaining:,}", delta=f"-¥{st.session_state.total_spent:,}")
        st.progress(min(st.session_state.total_spent / total_budget, 1.0))

    test_hotels = [
        {
            'id': 1,
            'name': 'Pudong Shangri-La Hotel, Shanghai',
            'location': 'Pudong New Area',
            'address': '33 Fucheng Road, Pudong New Area',
            'tel': '021-68828888',
            'rating': 4.8,
            'price': 680,
            'amenities': ['Free WiFi', 'Gym', 'Swimming Pool', 'Business Center', 'Parking', 'Breakfast']
        },
        {
            'id': 2,
            'name': 'Home Inn Express',
            'location': 'People\'s Square',
            'address': '123 Nanjing East Road, Huangpu District',
            'tel': '021-12345678',
            'rating': 4.2,
            'price': 299,
            'amenities': ['Free WiFi', '24-hour Front Desk']
        },
        {
            'id': 3,
            'name': 'Hanting Hotel',
            'location': 'Hongqiao Airport',
            'address': '888 Hongqiao Road, Minhang District',
            'tel': '021-87654321',
            'rating': 3.9,
            'price': 188,
            'amenities': ['Free WiFi', 'Buffet Breakfast']
        },
    ]

    def test_booking_callback(hotel, price):
        """Test booking callback"""
        st.session_state.total_spent += price
        nights = hotel.get('nights', 1)
        checkin = hotel.get('checkin_date')
        checkout = hotel.get('checkout_date')

        st.success(f"""
        ✅ Booking successful!
        
        - Hotel: {hotel['name']}
        - Check-in: {checkin.strftime('%Y-%m-%d')}
        - Check-out: {checkout.strftime('%Y-%m-%d')}
        - Nights: {nights}
        - Total price: ¥{price:,}
        - Remaining budget: ¥{get_remaining_budget():,}
        """)
        st.balloons()

    display_hotel_list_v2(test_hotels, message_id=0, on_book_callback=test_booking_callback)