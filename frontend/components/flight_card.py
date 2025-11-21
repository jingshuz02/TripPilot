"""
Simulated Flight Card Component - Unified Budget Version
Features:
1. Clear display of Origin -> Destination
2. Cabin selection (Economy, Business, First Class)
3. 💰 Unified budget check
4. ✅ Booking success pop-up
5. Light green color scheme
"""

import streamlit as st
from datetime import datetime


def get_remaining_budget():
    """Get remaining budget - consistent with chat.py"""
    if "current_trip" in st.session_state and "total_spent" in st.session_state:
        total_budget = st.session_state.current_trip.get("budget", 5000)
        return total_budget - st.session_state.total_spent
    return 0


def display_flight_card_v2(flight, key_prefix="flight", message_id=0, on_book_callback=None):
    """
    Simulated Flight Card Display - with Unified Budget Check

    Parameters:
        flight: Flight data dictionary
        key_prefix: Button key prefix
        message_id: Message ID
        on_book_callback: Booking callback function
    """

    st.markdown("""
    <style>
    .flight-card-realistic {
        background: #ffffff;
        border: 1px solid #d1d5db;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
        position: relative;
        z-index: 1;
    }
    
    .flight-card-realistic:hover {
        border-color: #10b981;
        box-shadow: 0 4px 12px rgba(10, 185, 129, 0.15);
    }
    
    .flight-route-display {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 16px;
        padding: 16px;
        background: linear-gradient(135deg, #f0fdf4 0%, #d1fae5 100%);
        border-radius: 10px;
    }
    
    .flight-city-info {
        flex: 1;
        text-align: center;
    }
    
    .flight-city-code {
        font-size: 28px;
        font-weight: 800;
        color: #047857;
        margin-bottom: 4px;
    }
    
    .flight-city-name {
        font-size: 13px;
        color: #6b7280;
    }
    
    .flight-arrow {
        font-size: 32px;
        color: #10b981;
        margin: 0 16px;
    }
    
    .flight-basic-info {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .flight-info-item {
        text-align: center;
        padding: 8px;
    }
    
    .flight-info-label {
        font-size: 12px;
        color: #6b7280;
        margin-bottom: 4px;
    }
    
    .flight-info-value {
        font-size: 16px;
        font-weight: 600;
        color: #111827;
    }
    
    .flight-airline-badge {
        display: inline-flex;
        align-items: center;
        background: #f3f4f6;
        color: #374151;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: 500;
        margin-right: 8px;
    }
    
    .flight-price-display {
        font-size: 28px;
        font-weight: 700;
        color: #10b981;
        line-height: 1;
    }
    
    .flight-cabin-notice {
        font-size: 12px;
        color: #6b7280;
        margin-top: 4px;
    }
    
    .budget-warning-flight {
        background: #fef3c7;
        border: 1px solid #f59e0b;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 13px;
        color: #92400e;
        margin-top: 8px;
    }
    
    .budget-ok-flight {
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

    flight_id = flight.get('id', 0)
    details_key = f"{key_prefix}_detail_{message_id}_{flight_id}"
    cabin_key = f"{key_prefix}_cabin_{message_id}_{flight_id}"
    book_key = f"{key_prefix}_book_{message_id}_{flight_id}"

    if details_key not in st.session_state:
        st.session_state[details_key] = False

    if cabin_key not in st.session_state:
        st.session_state[cabin_key] = "economy"

    # Cabin Price Configuration
    base_price = flight.get('price', flight.get('total_price', 0))
    cabin_prices = {
        "economy": {"name": "Economy Class", "price": base_price, "multiplier": 1.0},
        "business": {"name": "Business Class", "price": int(base_price * 2.5), "multiplier": 2.5},
        "first": {"name": "First Class", "price": int(base_price * 4.0), "multiplier": 4.0}
    }

    # ✅ Get remaining budget
    remaining_budget = get_remaining_budget()

    with st.container():
        st.markdown("<div class='flight-card-realistic'>", unsafe_allow_html=True)

        # Route Display
        origin = flight.get('origin', 'Origin')
        destination = flight.get('destination', 'Destination')

        origin_code = origin[:3].upper() if len(origin) <= 4 else origin[:3].upper()
        dest_code = destination[:3].upper() if len(destination) <= 4 else destination[:3].upper()

        st.markdown(f"""
        <div class='flight-route-display'>
            <div class='flight-city-info'>
                <div class='flight-city-code'>{origin_code}</div>
                <div class='flight-city-name'>{origin}</div>
            </div>
            <div class='flight-arrow'>✈</div>
            <div class='flight-city-info'>
                <div class='flight-city-code'>{dest_code}</div>
                <div class='flight-city-name'>{destination}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Basic Information
        carrier_name = flight.get('carrier_name', flight.get('carrier_code', 'Airline'))
        flight_number = flight.get('flight_number', 'XXXX')
        departure_time = flight.get('departure_time', 'N/A')
        arrival_time = flight.get('arrival_time', 'N/A')
        duration = flight.get('duration', 'N/A')
        departure_date = flight.get('departure_date', datetime.now().strftime('%Y-%m-%d'))

        col_airline, col_date = st.columns([2, 1])

        with col_airline:
            st.markdown(f"""
                <span class='flight-airline-badge'>{carrier_name} {flight_number}</span>
            """, unsafe_allow_html=True)

        with col_date:
            st.markdown(f"""
                <div style='text-align: right; font-size: 13px; color: #6b7280;'>
                    {departure_date}
                </div>
            """, unsafe_allow_html=True)

        # Time Information Card
        st.markdown(f"""
        <div class='flight-basic-info'>
            <div class='flight-info-item'>
                <div class='flight-info-label'>Departure Time</div>
                <div class='flight-info-value'>{departure_time}</div>
            </div>
            <div class='flight-info-item'>
                <div class='flight-info-label'>Flight Duration</div>
                <div class='flight-info-value'>{duration}</div>
            </div>
            <div class='flight-info-item'>
                <div class='flight-info-label'>Arrival Time</div>
                <div class='flight-info-value'>{arrival_time}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Cabin Selection and Price Display
        col_cabin, col_price, col_btn = st.columns([2, 1.5, 1.5])

        with col_cabin:
            st.markdown("**Select Cabin**")
            selected_cabin = st.selectbox(
                "Cabin",
                options=list(cabin_prices.keys()),
                format_func=lambda x: cabin_prices[x]["name"],
                key=cabin_key,
                label_visibility="collapsed"
            )

            cabin_info = {
                "economy": "Standard Seat • 20kg Baggage",
                "business": "Lie-flat Seat • 30kg Baggage • Lounge Access",
                "first": "Luxury Seat • 40kg Baggage • Exclusive Service"
            }
            st.caption(cabin_info[selected_cabin])

        with col_price:
            current_price = cabin_prices[selected_cabin]["price"]
            st.markdown(f"""
                <div style='text-align: right; padding-top: 8px;'>
                    <div class='flight-price-display'>¥{current_price:,}</div>
                    <div class='flight-cabin-notice'>{cabin_prices[selected_cabin]["name"]}</div>
                </div>
            """, unsafe_allow_html=True)

        with col_btn:
            st.markdown("<div style='padding-top: 8px;'></div>", unsafe_allow_html=True)

            button_text = "Hide Details" if st.session_state[details_key] else "View Details"
            if st.button(
                button_text,
                key=details_key + "_btn",
                use_container_width=True
            ):
                st.session_state[details_key] = not st.session_state[details_key]
                st.rerun()

            # ✅ Booking Button - with Budget Check
            can_afford = current_price <= remaining_budget

            if can_afford:
                if st.button(
                    "Book",
                    key=book_key,
                    type="primary",
                    use_container_width=True
                ):
                    if on_book_callback:
                        # Prepare flight data (including selected cabin)
                        flight_data = flight.copy()
                        flight_data['cabin_class'] = cabin_prices[selected_cabin]["name"]
                        flight_data['price'] = current_price

                        on_book_callback("flight", flight_data, current_price)
                        st.rerun()
                    else:
                        # Default behavior
                        st.session_state.total_spent = st.session_state.get("total_spent", 0) + current_price
                        st.success(f"""
                        ✅ Booking Successful!
                        
                        - Flight: {carrier_name} {flight_number}
                        - Cabin: {cabin_prices[selected_cabin]['name']}
                        - Price: ¥{current_price:,}
                        - Remaining Budget: ¥{get_remaining_budget():,}
                        """)
                        st.balloons()
                        st.rerun()
            else:
                st.button(
                    "Budget Insufficient",
                    key=book_key,
                    disabled=True,
                    use_container_width=True
                )

        # ✅ Budget Tip
        if not can_afford:
            st.markdown(f"""
                <div class='budget-warning-flight'>
                    💰 Budget Insufficient | Needed: ¥{current_price:,} | Remaining: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div class='budget-ok-flight'>
                    ✅ Budget Sufficient | Remaining: ¥{remaining_budget:,}
                </div>
            """, unsafe_allow_html=True)

        # Details Expansion Area
        if st.session_state[details_key]:
            st.markdown("""
            <div style='background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 8px; 
                        padding: 16px; margin-top: 12px;'>
            """, unsafe_allow_html=True)

            aircraft = flight.get('aircraft', 'Boeing 737')
            stops = flight.get('stops', 0)
            available_seats = flight.get('available_seats', 20)

            st.markdown(f"""
            <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                        border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>Flight Number</span>
                <span style='color: #111827; font-weight: 600;'>{carrier_name} {flight_number}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                        border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>Aircraft Type</span>
                <span style='color: #111827; font-weight: 600;'>{aircraft}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 8px 0; 
                        border-bottom: 1px solid #e5e7eb; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>Stops</span>
                <span style='color: #111827; font-weight: 600;'>{'Non-stop' if stops == 0 else f'{stops} stop{"s" if stops > 1 else ""}'}</span>
            </div>
            <div style='display: flex; justify-content: space-between; padding: 8px 0; font-size: 14px;'>
                <span style='color: #6b7280; font-weight: 500;'>Available Seats</span>
                <span style='color: #111827; font-weight: 600;'>{available_seats} seats</span>
            </div>
            """, unsafe_allow_html=True)

            # Cabin Comparison
            st.markdown("<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;'>",
                       unsafe_allow_html=True)
            st.markdown("<span style='color: #6b7280; font-weight: 500;'>Price Comparison by Cabin</span>", unsafe_allow_html=True)
            st.markdown("<div style='margin-top: 8px;'>", unsafe_allow_html=True)

            cols = st.columns(3)
            for idx, (cabin_type, cabin_data) in enumerate(cabin_prices.items()):
                with cols[idx]:
                    is_selected = cabin_type == selected_cabin
                    border_color = "#10b981" if is_selected else "#e5e7eb"
                    bg_color = "#f0fdf4" if is_selected else "#ffffff"

                    # ✅ Check if this cabin is affordable
                    cabin_can_afford = cabin_data['price'] <= remaining_budget

                    st.markdown(f"""
                    <div style='padding: 12px; border: 2px solid {border_color}; 
                                border-radius: 8px; text-align: center; background: {bg_color};'>
                        <div style='font-size: 13px; color: #6b7280; margin-bottom: 4px;'>
                            {cabin_data['name']}
                        </div>
                        <div style='font-size: 18px; font-weight: 700; color: {"#10b981" if cabin_can_afford else "#ef4444"};'>
                            ¥{cabin_data['price']:,}
                        </div>
                        <div style='font-size: 11px; color: {"#065f46" if cabin_can_afford else "#991b1b"};'>
                            {"✅ Affordable" if cabin_can_afford else "❌ Budget Insufficient"}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

            # Service Description
            st.markdown("<div style='margin-top: 12px; padding-top: 12px; border-top: 1px solid #e5e7eb;'>",
                       unsafe_allow_html=True)
            st.markdown("<span style='color: #6b7280; font-weight: 500;'>Service Description</span>", unsafe_allow_html=True)

            service_items = [
                "✓ Free Wi-Fi (select flights)",
                "✓ In-flight entertainment system",
                "✓ Meal and beverage service",
                "✓ Free rebooking (same day only)"
            ]

            for item in service_items:
                st.markdown(f"<div style='color: #374151; font-size: 13px; padding: 2px 0;'>{item}</div>",
                           unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return None


def display_flight_list_v2(flights, message_id=0, on_book_callback=None):
    """
    Flight List Display - with Unified Budget Management

    Parameters:
        flights: List of flights
        message_id: Message ID
        on_book_callback: Booking callback function
    """
    if not flights:
        st.info("No flights matching the criteria were found.")
        return

    # ✅ Display remaining budget
    remaining_budget = get_remaining_budget()

    col_result, col_budget = st.columns([2, 1])
    with col_result:
        st.markdown(f"""
        <div style='background: #d1fae5; border: 1px solid #10b981; border-radius: 8px; 
                    padding: 12px 16px; margin-bottom: 16px;'>
            <span style='color: #047857; font-size: 14px;'>
                Found <strong>{len(flights)}</strong> flights
            </span>
        </div>
        """, unsafe_allow_html=True)

    with col_budget:
        st.metric("💰 Remaining Budget", f"¥{remaining_budget:,}")

    # Filter
    with st.expander("Filter Options", expanded=False):
        col1, col2, col3 = st.columns(3)

        with col1:
            max_price = st.number_input(
                "Max Price (Yuan)",
                min_value=0,
                max_value=10000,
                value=min(5000, int(remaining_budget)) if remaining_budget > 0 else 5000,
                step=100,
                key=f"flight_price_{message_id}"
            )

        with col2:
            flight_time = st.selectbox(
                "Time Slot",
                options=["All", "Morning (06:00-12:00)", "Afternoon (12:00-18:00)", "Evening (18:00-24:00)"],
                key=f"flight_time_{message_id}"
            )

        with col3:
            stops_filter = st.selectbox(
                "Stops",
                options=["All", "Non-stop Only", "1 Stop"],
                key=f"flight_stops_{message_id}"
            )

    # Filter flights
    filtered = []
    for flight in flights:
        if flight.get('price', 0) > max_price:
            continue

        if flight_time != "All":
            dep_time = flight.get('departure_time', '00:00')
            hour = int(dep_time.split(':')[0])

            if flight_time == "Morning (06:00-12:00)" and not (6 <= hour < 12):
                continue
            elif flight_time == "Afternoon (12:00-18:00)" and not (12 <= hour < 18):
                continue
            elif flight_time == "Evening (18:00-24:00)" and not (18 <= hour < 24):
                continue

        stops = flight.get('stops', 0)
        if stops_filter == "Non-stop Only" and stops != 0:
            continue
        elif stops_filter == "1 Stop" and stops != 1:
            continue

        filtered.append(flight)

    if not filtered:
        st.warning("No flights match the filtering criteria.")
        return

    # Sorting options
    col_sort1, col_sort2 = st.columns([3, 1])
    with col_sort2:
        sort_by = st.selectbox(
            "Sort By",
            options=["Price: Low to High", "Price: High to Low", "Departure Time"],
            key=f"flight_sort_{message_id}",
            label_visibility="collapsed"
        )

    if sort_by == "Price: Low to High":
        filtered.sort(key=lambda x: x.get('price', 0))
    elif sort_by == "Price: High to Low":
        filtered.sort(key=lambda x: x.get('price', 0), reverse=True)
    elif sort_by == "Departure Time":
        filtered.sort(key=lambda x: x.get('departure_time', '00:00'))

    # Display flight cards
    for flight in filtered[:10]:
        display_flight_card_v2(
            flight,
            key_prefix="flight",
            message_id=message_id,
            on_book_callback=on_book_callback
        )


# Testing code
if __name__ == "__main__":
    st.set_page_config(page_title="Simulated Flight Card - Unified Budget Version", layout="wide")

    st.title("Simulated Flight Card Component - Unified Budget Version")
    st.caption("Demonstrates unified budget management and cabin selection")

    # Mock budget state
    if "total_spent" not in st.session_state:
        st.session_state.total_spent = 0

    if "current_trip" not in st.session_state:
        st.session_state.current_trip = {"budget": 5000}

    # Sidebar budget display
    with st.sidebar:
        st.header("💰 Budget Management")
        total_budget = st.session_state.current_trip["budget"]
        remaining = total_budget - st.session_state.total_spent

        st.metric("Total Budget", f"¥{total_budget:,}")
        st.metric("Remaining", f"¥{remaining:,}", delta=f"-¥{st.session_state.total_spent:,}")
        st.progress(min(st.session_state.total_spent / total_budget, 1.0))

    test_flights = [
        {
            'id': 1,
            'carrier_code': 'CA',
            'carrier_name': 'Air China',
            'flight_number': '1234',
            'origin': 'Beijing',
            'destination': 'Shanghai',
            'departure_time': '08:30',
            'arrival_time': '11:00',
            'departure_date': '2025-01-15',
            'duration': '2 hours 30 minutes',
            'price': 850,
            'aircraft': 'Boeing 737',
            'stops': 0,
            'available_seats': 25
        },
        {
            'id': 2,
            'carrier_code': 'MU',
            'carrier_name': 'China Eastern',
            'flight_number': '5678',
            'origin': 'Beijing',
            'destination': 'Shanghai',
            'departure_time': '14:15',
            'arrival_time': '16:50',
            'departure_date': '2025-01-15',
            'duration': '2 hours 35 minutes',
            'price': 720,
            'aircraft': 'Airbus A320',
            'stops': 0,
            'available_seats': 18
        }
    ]

    def test_booking_callback(order_type, flight, price):
        """Test booking callback"""
        st.session_state.total_spent += price
        st.success(f"""
        ✅ Booking Successful!
        
        - Flight: {flight['carrier_name']} {flight['flight_number']}
        - Cabin: {flight.get('cabin_class', 'N/A')}
        - Price: ¥{price:,}
        - Remaining Budget: ¥{get_remaining_budget():,}
        """)
        st.balloons()

    display_flight_list_v2(test_flights, message_id=0, on_book_callback=test_booking_callback)