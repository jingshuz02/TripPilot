"""
Amadeus API Service - Complete AI Enhanced Version
Handles flight and hotel searches, includes AI enhancement to fill missing data.
"""
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import re

from config.config import Config


class AmadeusService:
    """
    Amadeus Travel Service (Complete AI Enhanced Version)
    Provides flight and hotel search functions, intelligently fills missing data.
    """

    def __init__(self, deepseek_client=None):
        """Initialize Amadeus Service"""
        # API Configuration
        self.client_id = Config.AMADEUS_CLIENT_ID
        self.client_secret = Config.AMADEUS_CLIENT_SECRET
        self.base_url = "https://test.api.amadeus.com"

        # Token Management
        self.access_token = None
        self.token_expires_at = None

        # AI Enhancement
        self.deepseek_client = deepseek_client

        print("✅ Amadeus Service Initialized (AI Enhanced)")

    # ==================== Flight Search (AI Enhanced) ====================

    def search_flights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search Flights (AI Enhanced)
        Automatically fills missing flight information.
        """
        try:
            origin = params['origin']
            destination = params['destination']
            date = params['departure_date']

            print(f"\n✈️  Searching Flights: {origin} → {destination} ({date})")

            # Call Real API
            endpoint = f"{self.base_url}/v2/shopping/flight-offers"

            api_params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": date,
                "adults": params.get('adults', 1),
                "travelClass": params.get('travel_class', 'ECONOMY'),
                "nonStop": str(params.get('non_stop', False)).lower(),
                "currencyCode": "USD",
                "max": params.get('max_results', 10)
            }

            result = self._call_api(endpoint, api_params)

            if 'error' in result:
                return {
                    'success': False,
                    'data': [],
                    'count': 0,
                    'message': f"Search failed: {result['error']}"
                }

            # Extract and enhance flight data
            flights = result.get('data', [])
            enhanced_flights = []
            ai_enhanced_count = 0

            for flight in flights:
                enhanced_flight, is_ai_enhanced = self._enhance_flight_data(flight)
                enhanced_flights.append(enhanced_flight)
                if is_ai_enhanced:
                    ai_enhanced_count += 1

            print(f"✅ Found {len(enhanced_flights)} flights")
            if ai_enhanced_count > 0:
                print(f"   💡 AI enhanced data for {ai_enhanced_count} flights")

            return {
                'success': True,
                'data': enhanced_flights,
                'count': len(enhanced_flights),
                'ai_enhanced_count': ai_enhanced_count,
                'message': f"Found {len(enhanced_flights)} flights"
            }

        except KeyError as e:
            return {
                'success': False,
                'data': [],
                'count': 0,
                'message': f"Missing required parameters: {e}"
            }
        except Exception as e:
            print(f"❌ Flight search error: {e}")
            return {
                'success': False,
                'data': [],
                'count': 0,
                'message': f"Search error: {str(e)}"
            }

    def _enhance_flight_data(self, flight: Dict) -> tuple:
        """
        Enhance flight data, fill missing fields.

        Returns:
            (enhanced_flight, is_ai_enhanced)
        """
        try:
            itinerary = flight.get('itineraries', [{}])[0]
            segments = itinerary.get('segments', [])

            if not segments:
                return flight, False

            first_segment = segments[0]
            last_segment = segments[-1]

            # Get cabin and baggage info
            traveler_pricing = flight.get('travelerPricings', [{}])[0]
            fare_details = traveler_pricing.get('fareDetailsBySegment', [{}])[0]
            cabin_class = fare_details.get('cabin', 'ECONOMY')

            # Basic Data
            enhanced = {
                'id': flight.get('id'),
                'source': flight.get('source', 'GDS'),
                'price': {
                    'total': flight.get('price', {}).get('total'),
                    'base': flight.get('price', {}).get('base'),
                    'currency': flight.get('price', {}).get('currency', 'USD'),
                    'grandTotal': flight.get('price', {}).get('grandTotal')
                },
                'departure': {
                    'iataCode': first_segment.get('departure', {}).get('iataCode'),
                    'terminal': first_segment.get('departure', {}).get('terminal'),
                    'at': first_segment.get('departure', {}).get('at')
                },
                'arrival': {
                    'iataCode': last_segment.get('arrival', {}).get('iataCode'),
                    'terminal': last_segment.get('arrival', {}).get('terminal'),
                    'at': last_segment.get('arrival', {}).get('at')
                },
                'carrierCode': first_segment.get('carrierCode'),
                'number': first_segment.get('number'),
                'aircraft': first_segment.get('aircraft', {}).get('code'),
                'duration': itinerary.get('duration'),
                'numberOfStops': len(segments) - 1,
                'cabinClass': cabin_class  # Obtained from API response
            }

            # Check for missing fields and use AI to fill
            is_ai_enhanced = False
            missing_fields = []

            # Check critical fields
            if not enhanced.get('aircraft'):
                missing_fields.append('aircraft')
            if not enhanced['departure'].get('terminal'):
                missing_fields.append('departure_terminal')
            if not enhanced['arrival'].get('terminal'):
                missing_fields.append('arrival_terminal')

            # Get baggage allowance
            enhanced['includedCheckedBags'] = fare_details.get('includedCheckedBags', {}).get('quantity')
            enhanced['cabin'] = cabin_class

            if not enhanced.get('includedCheckedBags'):
                missing_fields.append('baggage')

            # If fields are missing and AI client exists, use AI to enhance
            if missing_fields and self.deepseek_client:
                ai_data = self._ai_enhance_flight(enhanced, missing_fields)
                if ai_data:
                    enhanced.update(ai_data)
                    enhanced['_ai_enhanced'] = True
                    enhanced['_ai_fields'] = missing_fields
                    is_ai_enhanced = True

            return enhanced, is_ai_enhanced

        except Exception as e:
            print(f"⚠️  Flight data enhancement failed: {e}")
            return flight, False

    def _ai_enhance_flight(self, flight_data: Dict, missing_fields: List[str]) -> Optional[Dict]:
        """Use AI to fill missing flight information"""
        if not self.deepseek_client:
            return None

        try:
            carrier = flight_data.get('carrierCode', '')
            aircraft_code = flight_data.get('aircraft', '')
            cabin_class = flight_data.get('cabinClass', 'ECONOMY')

            prompt = f"""Supply missing information for the flight.
Flight: {carrier}{flight_data.get('number', '')}
Aircraft: {aircraft_code if aircraft_code else 'Unknown'}
Cabin: {cabin_class}

Missing Fields: {', '.join(missing_fields)}

Return in JSON format, containing only reasonable values for missing fields:
{{
    "aircraft": "Aircraft Type Code (e.g., B787-8, A350-900)",
    "departure_terminal": "Terminal (e.g., T1, T2 or null)",
    "arrival_terminal": "Terminal",
    "includedCheckedBags": "Number of checked bags (1-3)",
    "amenities": [
        {{"service": "Service Name", "isChargeable": true/false}}
    ]
}}

Notes:
- If aircraft is known, keep it; if unknown, infer based on airline and route.
- Baggage allowance should match cabin class standards (Economy 1-2, Business 2-3).
- Amenities should match aircraft and airline characteristics.

Return only JSON, no other content."""

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Low temperature ensures accuracy
                max_tokens=500
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)

            if json_match:
                ai_data = json.loads(json_match.group())
                print(f"   💡 AI filled fields: {', '.join(missing_fields)}")
                return ai_data

            return None

        except Exception as e:
            print(f"⚠️  AI enhancement failed: {e}")
            return None

    # ==================== Hotel Search (AI Enhanced) ====================

    def search_hotels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search Hotels (With AI Enhancement)
        (Keeps original implementation, already AI enhanced)
        """
        try:
            lat = params['latitude']
            lon = params['longitude']
            check_in = params['check_in_date']
            check_out = params['check_out_date']

            print(f"\n🏨 Searching Hotels: ({lat}, {lon})")
            print(f"   Dates: {check_in} → {check_out}")

            # Step 1: Search basic hotel info
            hotels = self._search_hotels_basic(params)

            if not hotels:
                return {
                    'success': False,
                    'hotels': [],
                    'offers': [],
                    'reviews': [],
                    'count': 0,
                    'ai_enhanced': False,
                    'message': 'No hotels found'
                }

            print(f"✅ Found {len(hotels)} hotels")

            # Step 2: Get room offers (Real API + AI Supplement)
            offers, ai_offer_count = self._get_hotel_offers(hotels, params)
            print(f"   💰 Retrieved {len(offers)} offers (AI Generated: {ai_offer_count})")

            # Step 3: Get hotel reviews (Real API + AI Supplement)
            reviews, ai_review_count = self._get_hotel_reviews(hotels)
            print(f"   ⭐ Retrieved {len(reviews)} reviews (AI Generated: {ai_review_count})")

            ai_enhanced = ai_offer_count > 0 or ai_review_count > 0

            return {
                'success': True,
                'hotels': hotels,
                'offers': offers,
                'reviews': reviews,
                'count': len(hotels),
                'ai_enhanced': ai_enhanced,
                'message': f"Found {len(hotels)} hotels"
            }

        except Exception as e:
            print(f"❌ Hotel search error: {e}")
            return {
                'success': False,
                'hotels': [],
                'offers': [],
                'reviews': [],
                'count': 0,
                'ai_enhanced': False,
                'message': f"Search error: {str(e)}"
            }

    def _search_hotels_basic(self, params: Dict) -> List[Dict]:
        """Search basic hotel information"""
        endpoint = f"{self.base_url}/v1/reference-data/locations/hotels/by-geocode"

        api_params = {
            "latitude": params['latitude'],
            "longitude": params['longitude'],
            "radius": params.get('radius', 5),
            "radiusUnit": "KM"
        }

        result = self._call_api(endpoint, api_params)
        return result.get('data', []) if 'error' not in result else []

    def _get_hotel_offers(self, hotels: List[Dict], params: Dict) -> tuple:
        """Get hotel offers (Real API + AI Supplement)"""
        all_offers = []
        ai_count = 0

        for hotel in hotels[:5]:
            hotel_id = hotel.get('hotelId')

            endpoint = f"{self.base_url}/v3/shopping/hotel-offers"
            api_params = {
                "hotelIds": hotel_id,
                "checkInDate": params.get('check_in_date'),
                "checkOutDate": params.get('check_out_date'),
                "adults": params.get('adults', 2),
                "bestRateOnly": "true"
            }

            result = self._call_api(endpoint, api_params)

            if 'data' in result and result['data']:
                all_offers.extend(result['data'])
            else:
                if self.deepseek_client:
                    ai_offer = self._generate_hotel_offer(hotel, params)
                    if ai_offer:
                        all_offers.append(ai_offer)
                        ai_count += 1

        return all_offers, ai_count

    def _get_hotel_reviews(self, hotels: List[Dict]) -> tuple:
        """Get hotel reviews (Real API + AI Supplement)"""
        all_reviews = []
        ai_count = 0

        for hotel in hotels[:5]:
            hotel_id = hotel.get('hotelId')

            endpoint = f"{self.base_url}/v2/e-reputation/hotel-sentiments"
            api_params = {"hotelIds": hotel_id}

            result = self._call_api(endpoint, api_params)

            if 'data' in result and result['data']:
                all_reviews.extend(result['data'])
            else:
                if self.deepseek_client:
                    ai_review = self._generate_hotel_review(hotel)
                    if ai_review:
                        all_reviews.append(ai_review)
                        ai_count += 1

        return all_reviews, ai_count

    def _generate_hotel_offer(self, hotel: Dict, params: Dict) -> Optional[Dict]:
        """Use AI to generate hotel offers"""
        if not self.deepseek_client:
            return None

        try:
            hotel_id = hotel.get('hotelId')
            hotel_name = hotel.get('name', 'Hotel')

            prompt = f"""Generate reasonable room offers for the hotel (Demo Data).
Hotel: {hotel_name}
Check-in: {params.get('check_in_date')}
Check-out: {params.get('check_out_date')}

Return JSON:
{{
    "room_type": "Room Type Name",
    "price": Price per night in USD (100-400),
    "description": "30-word description"
}}

Return only JSON."""

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)

            if json_match:
                ai_data = json.loads(json_match.group())
                return {
                    "type": "hotel-offers",
                    "hotel": {"hotelId": hotel_id, "name": hotel_name},
                    "available": True,
                    "offers": [{
                        "id": f"ai-{hotel_id}-{int(datetime.now().timestamp())}",
                        "checkInDate": params.get('check_in_date'),
                        "checkOutDate": params.get('check_out_date'),
                        "room": {
                            "type": ai_data['room_type'],
                            "description": {"text": ai_data['description']}
                        },
                        "price": {
                            "currency": "USD",
                            "total": str(ai_data['price']),
                            "base": str(ai_data['price'])
                        },
                        "_source": "ai_generated"
                    }]
                }

            return None

        except Exception as e:
            print(f"⚠️  AI offer generation failed: {e}")
            return None

    def _generate_hotel_review(self, hotel: Dict) -> Optional[Dict]:
        """Use AI to generate hotel reviews"""
        if not self.deepseek_client:
            return None

        try:
            hotel_id = hotel.get('hotelId')

            prompt = f"""Generate hotel sentiment data.
Return JSON:
{{
    "overall_rating": 60-95,
    "number_of_reviews": 80-300,
    "sleep_quality": 60-95,
    "service": 60-95,
    "facilities": 60-95,
    "location": 60-95
}}

Return only JSON."""

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)

            if json_match:
                ai_data = json.loads(json_match.group())
                return {
                    "type": "hotelSentiment",
                    "hotelId": hotel_id,
                    "overallRating": ai_data['overall_rating'],
                    "numberOfReviews": ai_data['number_of_reviews'],
                    "sentiments": {
                        "sleepQuality": ai_data['sleep_quality'],
                        "service": ai_data['service'],
                        "facilities": ai_data['facilities'],
                        "location": ai_data['location']
                    },
                    "_source": "ai_generated"
                }

            return None

        except Exception as e:
            print(f"⚠️  AI review generation failed: {e}")
            return None

    # ==================== Token Management ====================

    def _get_amadeus_token(self) -> str:
        """Get Amadeus Access Token"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        print("🔑 Getting Amadeus Token...")

        url = f"{self.base_url}/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']

            expires_in = token_data.get('expires_in', 1799)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            print("✅ Token acquired successfully")
            return self.access_token

        except Exception as e:
            raise Exception(f"Cannot get Amadeus token: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """Get API Request Headers"""
        access_token = self._get_amadeus_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def _call_api(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generic API Call"""
        try:
            headers = self._get_headers()
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)

            if response.status_code == 401:
                print("🔄 Token expired, refreshing...")
                self.access_token = None
                headers = self._get_headers()
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ API Request Error: {e}")
            return {"error": str(e)}