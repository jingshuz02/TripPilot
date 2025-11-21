"""
Booking Tools - Amadeus API Wrapper
Provides simple booking interfaces for the Agent.
"""
from backend.booking import AmadeusService
from config.config import Config
from datetime import date, timedelta


class BookingTool:
    """
    Booking Tool Class
    Wraps flight and hotel search functionality for Agent use.
    """

    def __init__(self):
        """Initialize Booking Tool"""
        # Initialize DeepSeek client (for AI enhancement)
        self.deepseek_client = Config.get_deepseek_client()

        # Create Amadeus service
        self.amadeus = AmadeusService(self.deepseek_client)

        print("✅ Booking Tool Initialization Complete")

    # ==================== Flight Search ====================

    def search_flights(self, origin: str, destination: str, date: str, **kwargs) -> dict:
        """
        Search for flights

        Args:
            origin: Departure IATA code (e.g., 'HKG')
            destination: Destination IATA code (e.g., 'NRT')
            date: Departure date (YYYY-MM-DD format)
            **kwargs: Other optional parameters
                - adults: Number of adults, default 1
                - travel_class: Cabin class (ECONOMY/BUSINESS/FIRST), default ECONOMY
                - non_stop: Whether to search for non-stop flights only, default True
                - max_results: Maximum number of results to return, default 10

        Returns:
            {
                'success': True/False,
                'data': [...],      # List of flights
                'count': 5,         # Number of flights found
                'message': 'Found 5 flights'
            }

        Example:
            >>> tool = BookingTool()
            >>> result = tool.search_flights('HKG', 'NRT', '2025-12-01')
            >>> if result['success']:
            >>>     print(f"Found {result['count']} flights")
            >>>     for flight in result['data']:
            >>>         print(f"Price: ${flight['price']['total']}")
        """
        params = {
            'origin': origin,
            'destination': destination,
            'departure_date': date,
            'adults': kwargs.get('adults', 1),
            'travel_class': kwargs.get('travel_class', 'ECONOMY'),
            'non_stop': kwargs.get('non_stop', True),
            'max_results': kwargs.get('max_results', 10)
        }

        return self.amadeus.search_flights(params)

    # ==================== Hotel Search ====================

    def search_hotels(self, latitude: float, longitude: float,
                     check_in: str, check_out: str, **kwargs) -> dict:
        """
        Search for hotels (by coordinates)

        Args:
            latitude: Latitude
            longitude: Longitude
            check_in: Check-in date (YYYY-MM-DD format)
            check_out: Check-out date (YYYY-MM-DD format)
            **kwargs: Other optional parameters
                - radius: Search radius (kilometers), default 5
                - adults: Number of adults, default 2

        Returns:
            {
                'success': True/False,
                'hotels': [...],        # Basic hotel information
                'offers': [...],        # Room offers
                'reviews': [...],       # Hotel reviews
                'count': 12,            # Number of hotels found
                'ai_enhanced': True,    # Whether AI enhancement was used
                'message': 'Found 12 hotels'
            }

        Example:
            >>> tool = BookingTool()
            >>> result = tool.search_hotels(
            ...     latitude=35.6762,
            ...     longitude=139.6503,
            ...     check_in='2025-12-01',
            ...     check_out='2025-12-05'
            ... )
            >>> if result['success']:
            >>>     print(result['message'])
            >>>     for hotel in result['hotels']:
            >>>         print(f"Hotel: {hotel['name']}")
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'radius': kwargs.get('radius', 5),
            'adults': kwargs.get('adults', 2)
        }

        return self.amadeus.search_hotels(params)

    def search_hotels_by_city(self, city: str, check_in: str, check_out: str, **kwargs) -> dict:
        """
        Search for hotels (by city name)

        Args:
            city: City name (e.g., 'Tokyo' or 'Shanghai')
            check_in: Check-in date (YYYY-MM-DD format)
            check_out: Check-out date (YYYY-MM-DD format)
            **kwargs: Other optional parameters (same as search_hotels)

        Returns:
            Same return format as search_hotels

        Example:
            >>> tool = BookingTool()
            >>> result = tool.search_hotels_by_city('Tokyo', '2025-12-01', '2025-12-05')
        """
        # City coordinate mapping table
        CITY_COORDS = {
            # Japan
            '东京': (35.6762, 139.6503),
            'Tokyo': (35.6762, 139.6503),
            '大阪': (34.6937, 135.5023),
            'Osaka': (34.6937, 135.5023),
            '京都': (35.0116, 135.7681),
            'Kyoto': (35.0116, 135.7681),

            # China
            '北京': (39.9042, 116.4074),
            'Beijing': (39.9042, 116.4074),
            '上海': (31.2304, 121.4737),
            'Shanghai': (31.2304, 121.4737),
            '香港': (22.3193, 114.1694),
            'Hong Kong': (22.3193, 114.1694),
            '广州': (23.1291, 113.2644),
            'Guangzhou': (23.1291, 113.2644),
            '深圳': (22.5431, 114.0579),
            'Shenzhen': (22.5431, 114.0579),

            # Other Popular Cities
            '新加坡': (1.3521, 103.8198),
            'Singapore': (1.3521, 103.8198),
            '曼谷': (13.7563, 100.5018),
            'Bangkok': (13.7563, 100.5018),
            '首尔': (37.5665, 126.9780),
            'Seoul': (37.5665, 126.9780),

            # More cities can be added...
        }

        if city in CITY_COORDS:
            lat, lon = CITY_COORDS[city]
            return self.search_hotels(lat, lon, check_in, check_out, **kwargs)
        else:
            return {
                'success': False,
                'hotels': [],
                'offers': [],
                'reviews': [],
                'count': 0,
                'ai_enhanced': False,
                'message': f"Coordinates for city '{city}' not found. Please search using coordinates or add the city."
            }

    # ==================== Convenience Methods ====================

    def get_flight_price(self, origin: str, destination: str, date: str) -> dict:
        """
        Quickly get flight price (returns only the cheapest)

        Returns:
            {
                'success': True/False,
                'cheapest_price': 500.00,
                'currency': 'USD',
                'message': 'Cheapest price: $500.00'
            }
        """
        result = self.search_flights(origin, destination, date, max_results=5)

        if result['success'] and result['data']:
            prices = [float(f['price']['total']) for f in result['data'] if 'price' in f]
            if prices:
                cheapest = min(prices)
                return {
                    'success': True,
                    'cheapest_price': cheapest,
                    'currency': 'USD',
                    'message': f"Cheapest price: ${cheapest:.2f}"
                }

        return {
            'success': False,
            'cheapest_price': None,
            'currency': 'USD',
            'message': 'No price information found'
        }

    def get_hotel_count(self, city: str) -> dict:
        """
        Quickly get the number of hotels in a city

        Returns:
            {
                'success': True/False,
                'count': 12,
                'message': 'Found 12 hotels'
            }
        """
        # Use tomorrow as check-in date
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        checkout = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')

        result = self.search_hotels_by_city(city, tomorrow, checkout)

        return {
            'success': result['success'],
            'count': result['count'],
            'message': result['message']
        }