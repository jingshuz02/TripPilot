"""
Response Formatter
Converts backend data into a unified format required by the frontend.

Frontend Expected Format:
{
  "action": "search_flights/search_hotels/get_weather/suggestion",
  "content": "Descriptive Text",
  "data": Structured Data or null
}

Author: Zeng Jingshu
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class ResponseFormatter:
    """Response Format Converter"""
    
    @staticmethod
    def format_flights(flights_data: Dict, query_context: str = "") -> Dict:
        """
        Format flight data
        
        Args:
            flights_data: Flight data returned by Amadeus
            query_context: Query context (e.g., "flying to Tokyo")
        """
        if not flights_data.get('success') or not flights_data.get('data'):
            return {
                "action": "search_flights",
                "content": "Sorry, no flights matching the criteria were found.",
                "data": []
            }
        
        flights = flights_data['data']
        count = len(flights)
        
        # Generate descriptive text
        content = f"Found the following {count} {query_context} flights."
        if flights_data.get('ai_enhanced_count', 0) > 0:
            content += f" (Data for {flights_data['ai_enhanced_count']} flights was partially supplemented by AI)"
        
        # Convert to frontend format
        formatted_flights = []
        for flight in flights:
            formatted_flight = {
                "id": flight.get('id', 'unknown'),
                "departure_iata": flight.get('departure', {}).get('iataCode'),
                "arrival_iata": flight.get('arrival', {}).get('iataCode'),
                "departure_time": flight.get('departure', {}).get('at'),
                "arrival_time": flight.get('arrival', {}).get('at'),
                "duration": ResponseFormatter._format_duration(flight.get('duration')),
                "carrier_code": flight.get('carrierCode'),
                "flight_number": str(flight.get('number', '')),
                "aircraft_code": flight.get('aircraft'),
                "operating_carrier": ResponseFormatter._get_airline_name(flight.get('carrierCode')),
                "cabin_class": flight.get('cabinClass', 'ECONOMY'),
                "currency": flight.get('price', {}).get('currency', 'USD'),
                "total_price": float(flight.get('price', {}).get('total', 0)),
                "base_price": float(flight.get('price', {}).get('base', 0)),
                "grand_total": float(flight.get('price', {}).get('grandTotal', 0)),
                "number_of_bookable_seats": 9,  # Amadeus test environment usually doesn't return this
                "last_ticketing_date": ResponseFormatter._get_ticketing_date(),
                "included_checked_bags": ResponseFormatter._format_baggage(
                    flight.get('includedCheckedBags'),
                    flight.get('cabinClass')
                ),
                "included_cabin_bags": "1 piece (7KG)",  # Standard value
                "amenities": flight.get('amenities', ResponseFormatter._get_default_amenities(
                    flight.get('carrierCode'),
                    flight.get('cabinClass')
                ))
            }
            
            # Mark AI-enhanced data
            if flight.get('_ai_enhanced'):
                formatted_flight['_ai_enhanced'] = True
                formatted_flight['_ai_fields'] = flight.get('_ai_fields', [])
            
            formatted_flights.append(formatted_flight)
        
        return {
            "action": "search_flights",
            "content": content,
            "data": formatted_flights
        }
    
    @staticmethod
    def format_hotels(hotels_data: Dict, query_context: str = "") -> Dict:
        """
        Format hotel data
        
        Args:
            hotels_data: Hotel data returned by Amadeus
            query_context: Query context (e.g., "located in Shinjuku")
        """
        if not hotels_data.get('success') or not hotels_data.get('hotels'):
            return {
                "action": "search_hotels",
                "content": "Sorry, no hotels matching the criteria were found.",
                "data": []
            }
        
        hotels = hotels_data['hotels']
        offers = hotels_data.get('offers', [])
        reviews = hotels_data.get('reviews', [])
        count = len(hotels)
        
        # Generate descriptive text
        content = f"Found the following {count} {query_context} hotels."
        if hotels_data.get('ai_enhanced'):
            content += " (Some data supplemented by AI generation)"
        
        # Build hotel details dictionary
        hotel_details = {}
        for hotel in hotels:
            hotel_id = hotel.get('hotelId')
            hotel_details[hotel_id] = {
                "id": hotel_id,
                "name": hotel.get('name', 'Unknown Hotel'),
                "location": hotel.get('address', {}).get('cityName', ''),
                "rating": 0,  # Obtained from reviews
                "desc": "",
                "price": 0,
                "nights": 0,
                "total_price": 0,
                "amenities": []
            }
        
        # Fill in price information
        for offer in offers:
            hotel_id = offer.get('hotel', {}).get('hotelId')
            if hotel_id in hotel_details:
                offer_data = offer.get('offers', [{}])[0]
                price = float(offer_data.get('price', {}).get('total', 0))
                hotel_details[hotel_id]['price'] = price
                hotel_details[hotel_id]['desc'] = offer_data.get('room', {}).get('description', {}).get('text', '')
                
                # Mark AI generation
                if offer_data.get('_source') == 'ai_generated':
                    hotel_details[hotel_id]['_ai_enhanced'] = True
        
        # Fill in review information
        for review in reviews:
            hotel_id = review.get('hotelId')
            if hotel_id in hotel_details:
                rating = review.get('overallRating', 0)
                hotel_details[hotel_id]['rating'] = round(rating / 20, 1)  # Convert to 5-star scale
        
        # Convert to list
        formatted_hotels = list(hotel_details.values())
        
        return {
            "action": "search_hotels",
            "content": content,
            "data": formatted_hotels
        }
    
    @staticmethod
    def format_weather(weather_data: Dict, city: str) -> Dict:
        """
        Format weather data
        
        Args:
            weather_data: Data returned by the weather API
            city: City name
        """
        if not weather_data or 'error' in weather_data:
            return {
                "action": "get_weather",
                "content": f"Sorry, unable to fetch weather information for {city}.",
                "data": None
            }
        
        # Generate descriptive text
        temp = weather_data.get('temperature', 0)
        desc = weather_data.get('weather', 'unknown')
        content = f"The weather in {city} is {desc}, current temperature {temp}°C."
        
        # Format data
        formatted_weather = {
            "city_name": city,
            "temperature": temp,
            "feels_like": weather_data.get('temperature', temp),
            "description": desc,
            "humidity": weather_data.get('humidity', 50),
            "wind_speed": weather_data.get('windspeed', 0),
            "icon": ResponseFormatter._get_weather_icon(desc)
        }
        
        return {
            "action": "get_weather",
            "content": content,
            "data": formatted_weather
        }
    
    @staticmethod
    def format_suggestion(suggestion_text: str, ai_enhanced: bool = False) -> Dict:
        """
        Format AI suggestion/Q&A
        Used for travel plans, isolated questions, etc.
        
        Args:
            suggestion_text: AI generated suggestion text
            ai_enhanced: Whether to mark as AI generated
        """
        content = suggestion_text
        if ai_enhanced:
            content += "\n\n_💡 This suggestion was intelligently generated by AI_"
        
        return {
            "action": "suggestion",
            "content": content,
            "data": None
        }
    
    # ==================== Helper Methods ====================
    
    @staticmethod
    def _format_duration(duration: str) -> str:
        """
        Format duration
        PT4H30M → 4h 30m
        """
        if not duration:
            return "unknown"
        
        import re
        hours = re.search(r'(\d+)H', duration)
        minutes = re.search(r'(\d+)M', duration)
        
        result = ""
        if hours:
            result += f"{hours.group(1)}h "
        if minutes:
            result += f"{minutes.group(1)}m"
        
        return result.strip() or "unknown"
    
    @staticmethod
    def _get_airline_name(carrier_code: str) -> str:
        """Get airline name"""
        airline_names = {
            "CX": "Cathay Pacific",
            "JL": "Japan Airlines",
            "NH": "All Nippon Airways",
            "CA": "Air China",
            "CZ": "China Southern",
            "MU": "China Eastern",
            "HX": "Hong Kong Airlines",
            "KE": "Korean Air",
            "OZ": "Asiana Airlines",
            "SQ": "Singapore Airlines",
            "TG": "Thai Airways",
            # Can add more
        }
        return airline_names.get(carrier_code, f"Airline {carrier_code}")
    
    @staticmethod
    def _get_ticketing_date() -> str:
        """Get ticketing deadline date (usually tomorrow)"""
        from datetime import date, timedelta
        tomorrow = date.today() + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    
    @staticmethod
    def _format_baggage(baggage_data: Any, cabin_class: str) -> str:
        """Format baggage allowance"""
        if isinstance(baggage_data, int):
            return f"{baggage_data} pieces (23KG)"
        
        # Return standard value based on cabin class
        if cabin_class == "BUSINESS":
            return "3 pieces (32KG)"
        elif cabin_class == "FIRST":
            return "3 pieces (32KG)"
        else:  # ECONOMY
            return "2 pieces (23KG)"
    
    @staticmethod
    def _get_default_amenities(carrier_code: str, cabin_class: str) -> List[Dict]:
        """Get default amenities (when API doesn't return them)"""
        if cabin_class == "BUSINESS":
            return [
                {"service": "Full Wi-Fi coverage", "isChargeable": False},
                {"service": "In-flight meal service", "isChargeable": False},
                {"service": "Lie-flat seat", "isChargeable": False}
            ]
        elif cabin_class == "FIRST":
            return [
                {"service": "Full Wi-Fi coverage", "isChargeable": False},
                {"service": "Michelin-star dining", "isChargeable": False},
                {"service": "Private suite", "isChargeable": False}
            ]
        else:  # ECONOMY
            return [
                {"service": "High-speed Wi-Fi", "isChargeable": True},
                {"service": "In-flight meal service", "isChargeable": False},
                {"service": "USB charging port", "isChargeable": False}
            ]
    
    @staticmethod
    def _get_weather_icon(description: str) -> str:
        """Return icon name based on weather description"""
        desc_lower = description.lower()
        
        if '晴' in desc_lower or 'sunny' in desc_lower or 'clear' in desc_lower:
            return "sunny"
        elif '云' in desc_lower or 'cloud' in desc_lower:
            return "cloudy"
        elif '雨' in desc_lower or 'rain' in desc_lower:
            return "rainy"
        elif '雪' in desc_lower or 'snow' in desc_lower:
            return "snowy"
        else:
            return "sunny"


# ==================== Usage Example ====================

if __name__ == "__main__":
    # Example: Format flight data
    sample_flight_data = {
        'success': True,
        'data': [{
            'id': 'fl_001',
            'departure': {'iataCode': 'HKG', 'at': '2025-11-20T09:00:00'},
            'arrival': {'iataCode': 'NRT', 'at': '2025-11-20T14:30:00'},
            'carrierCode': 'CX',
            'number': '504',
            'aircraft': 'A350-900',
            'duration': 'PT4H30M',
            'cabinClass': 'ECONOMY',
            'price': {'total': '450.50', 'base': '400.00', 'currency': 'USD'}
        }],
        'count': 1
    }
    
    formatter = ResponseFormatter()
    result = formatter.format_flights(sample_flight_data, "flights to Tokyo")
    
    import json
    # Setting ensure_ascii=True for clean output in English environment
    print(json.dumps(result, indent=2))