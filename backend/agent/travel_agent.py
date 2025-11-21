"""
TripPilot Travel Agent - Improved Version
New Features:
1. 🎯 Intelligent Budget Allocation
2. 💰 Price Reasonableness Check
3. 📊 Dynamic Recommendation Adjustment based on Remaining Budget
4. ✅ Ensure recommended prices do not exhaust the entire budget
"""

import json
import time
import random
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from config.config import Config

class TravelAgent:
    """Intelligent Travel Assistant Agent"""

    def __init__(self):
        """Initialize Agent"""
        print("🚀 Initializing TripPilot Agent...")

        self.config = Config()
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_BASE_URL
        self.model = Config.DEEPSEEK_MODEL

        self.init_tools()
        self.conversation_history = []

        print("✅ Agent Initialization Complete!\n")

    def init_tools(self):
        """Initialize Tools"""
        tools_status = []

        if Config.GAODE_API_KEY:
            tools_status.append("  Gaode API: ✅ Configured")
        else:
            tools_status.append("  Gaode API: ❌ Not Configured")

        if self.api_key:
            tools_status.append("  DeepSeek: ✅ Configured")
        else:
            tools_status.append("  DeepSeek: ❌ Not Configured")

        for status in tools_status:
            print(status)

        print("✅ Tools Initialization Complete")

        if self.api_key:
            print(f"✅ DeepSeek API Configured")
            print(f"   Key Prefix: {self.api_key[:12]}...")

    # ✅ New: Calculate Reasonable Budget Allocation
    def _calculate_budget_allocation(self, total_budget: float, remaining_budget: float, days: int) -> Dict[str, float]:
        """
        Calculate reasonable budget allocation

        Args:
            total_budget: Total budget
            remaining_budget: Remaining budget
            days: Number of travel days

        Returns:
            Budget allocation suggestions (flight, hotel, other)
        """
        # If remaining budget is low, return conservative suggestion
        if remaining_budget < total_budget * 0.3:
            return {
                "flight_max": remaining_budget * 0.3,
                "hotel_per_night_max": (remaining_budget * 0.4) / max(days - 1, 1),
                "other": remaining_budget * 0.3
            }

        # Normal case: 40% transport, 30% accommodation, 30% other
        return {
            "flight_max": remaining_budget * 0.4,
            "hotel_per_night_max": (remaining_budget * 0.3) / max(days - 1, 1),
            "other": remaining_budget * 0.3
        }

    def process_message(self, message: str, preferences: Dict = None) -> Dict:
        """Process user message"""
        print("=" * 60)
        print(f"📥 Received user message: {message}")

        if preferences:
            context = self._build_context(message, preferences)
        else:
            context = message

        intent = self._identify_intent(message)
        print(f"🎯 Identified Intent: {intent}")

        if intent == "full_planning":
            return self._handle_full_planning(context, preferences)
        elif intent == "search_hotels":
            return self._handle_hotel_search(context, preferences)
        elif intent == "search_flights":
            return self._handle_flight_search(context, preferences)
        elif intent == "weather":
            return self._handle_weather_query(context, preferences)
        elif intent == "attraction":
            return self._handle_attraction_query(context, preferences)
        else:
            return self._handle_general_query(context, preferences)

    def _build_context(self, message: str, preferences: Dict) -> str:
        """Build context information"""
        context_parts = [message]

        if preferences:
            if preferences.get("destination"):
                context_parts.append(f"Destination: {preferences['destination']}")
            if preferences.get("budget"):
                context_parts.append(f"Total Budget: ¥{preferences['budget']}")
            # ✅ Add remaining budget info
            if preferences.get("remaining_budget") is not None:
                context_parts.append(f"Remaining Budget: ¥{preferences['remaining_budget']}")
            if preferences.get("start_date") and preferences.get("end_date"):
                context_parts.append(f"Dates: {preferences['start_date']} to {preferences['end_date']}")

        return " | ".join(context_parts)

    def _identify_intent(self, message: str) -> str:
        """Identify user intent"""
        message_lower = message.lower()

        # Translated keywords to recognize English input
        intent_keywords = {
            "full_planning": ["plan", "itinerary", "arrange", "schedule", "play", "trip", "travel", "tour", "day trip"],
            "search_hotels": ["hotel", "accommodation", "inn", "hostel", "stay", "lodging"],
            "search_flights": ["flight", "ticket", "plane", "fly", "airline"],
            "weather": ["weather", "temperature", "rain", "temp", "wear", "forecast"],
            "attraction": ["attraction", "sightseeing", "where to go", "recommend", "must-see", "visit"]
        }

        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "general"

    def _handle_hotel_search(self, context: str, preferences: Dict) -> Dict:
        """Handle hotel search - with smart budget control"""

        # ✅ Get budget information
        total_budget = preferences.get("budget", 5000) if preferences else 5000
        remaining_budget = preferences.get("remaining_budget", total_budget) if preferences else total_budget
        days = preferences.get("days", 3) if preferences else 3

        # ✅ Calculate reasonable hotel price range
        budget_allocation = self._calculate_budget_allocation(total_budget, remaining_budget, days)
        max_hotel_price = int(budget_allocation["hotel_per_night_max"])

        # Ensure reasonable price (min 100, max not exceeding 40% of remaining budget)
        max_hotel_price = max(100, min(max_hotel_price, int(remaining_budget * 0.4)))

        # ✅ Modify prompt, ask DeepSeek to return reasonably priced hotels
        prompt = f"""
You are a professional hotel recommendation assistant. User Request: {context}

🎯 Important Budget Information:
- User Total Budget: ¥{total_budget}
- Remaining Budget: ¥{remaining_budget}
- Travel Days: {days} days
- Suggested Max Hotel Budget per Night: within ¥{max_hotel_price}

⚠️ Please Note:
1. Recommended hotel prices should not be too high; leave enough budget for dining and entertainment.
2. Price should be controlled between ¥100 - ¥{max_hotel_price}/night.
3. Recommend high value-for-money options, not just the most expensive ones.

Please return in the following format, starting with a natural language introduction, then providing JSON data:

【Text Introduction】
(Write recommendation reasons and explanation here, explaining why these hotels offer high value)

【JSON Data】
```json
{{
  "hotels": [
    {{
      "id": "hotel_001",
      "name": "Hotel Name",
      "location": "Location",
      "address": "Detailed Address",
      "tel": "Phone",
      "price": Price Number (controlled within {max_hotel_price}),
      "rating": Rating Number,
      "amenities": ["Amenity1", "Amenity2"],
      "landmark": "Landmark Description",
      "description": "Short Description"
    }}
  ]
}}
```

Requirements:
1. Recommend 5 real existing hotels.
2. Price must be between ¥100-¥{max_hotel_price}, considering the user's remaining budget.
3. Prioritize high value-for-money mid-range hotels.
4. JSON format must be strictly followed, no syntax errors.
5. Every field must be filled completely.
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")

            # ✅ Extract JSON data
            hotels_data = self._extract_json_from_response(content, "hotels")

            if hotels_data:
                # ✅ Filter overpriced hotels
                filtered_hotels = [
                    hotel for hotel in hotels_data
                    if 100 <= hotel.get('price', 0) <= max_hotel_price * 1.2  # Allow 20% buffer
                ]

                # If no hotels left after filtering, use original data but reduce price
                if not filtered_hotels:
                    filtered_hotels = self._adjust_hotel_prices(hotels_data, max_hotel_price)

                print(f"✅ Successfully extracted {len(filtered_hotels)} hotel data entries (prices filtered)")

                # ✅ Extract text part (content before JSON)
                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON Data】", "").replace("【Text Introduction】", "").strip()

                return {
                    "action": "search_hotels",
                    "content": text_part + f"\n\n💡 **Budget Tip**: Suggested hotel budget per night is ¥{max_hotel_price}. We selected high-value options for you.",
                    "data": filtered_hotels,
                    "suggestions": [
                        "View more hotels",
                        "Adjust price range",
                        "View user reviews"
                    ]
                }
            else:
                # ✅ If extraction fails, return text but give warning
                print("⚠️ Failed to extract JSON data, using fallback")
                return {
                    "action": "search_hotels",
                    "content": content + "\n\n⚠️ Failed to get structured data, please try searching again.",
                    "data": self._generate_smart_mock_hotels(preferences, max_hotel_price),
                    "suggestions": ["Search again", "Change criteria"]
                }
        else:
            return self._generate_fallback_response("hotel", context, preferences)

    def _handle_flight_search(self, context: str, preferences: Dict) -> Dict:
        """Handle flight search - with smart budget control"""

        # ✅ Get budget information
        total_budget = preferences.get("budget", 5000) if preferences else 5000
        remaining_budget = preferences.get("remaining_budget", total_budget) if preferences else total_budget
        days = preferences.get("days", 3) if preferences else 3

        # ✅ Calculate reasonable flight price range
        budget_allocation = self._calculate_budget_allocation(total_budget, remaining_budget, days)
        max_flight_price = int(budget_allocation["flight_max"])

        # Ensure reasonable price (min 200, max not exceeding 50% of remaining budget)
        max_flight_price = max(200, min(max_flight_price, int(remaining_budget * 0.5)))

        prompt = f"""
You are a professional flight search assistant. User Request: {context}

🎯 Important Budget Information:
- User Total Budget: ¥{total_budget}
- Remaining Budget: ¥{remaining_budget}
- Suggested Flight Budget: within ¥{max_flight_price}

⚠️ Please Note:
1. Recommended flight prices must be reasonable; do not spend the entire budget on tickets.
2. Price should be controlled between ¥200 - ¥{max_flight_price}.
3. Prioritize Economy Class; Business and First Class are too expensive.

Please return in the following format:

【Text Introduction】
(Write flight recommendation explanation here, emphasizing value)

【JSON Data】
```json
{{
  "flights": [
    {{
      "id": "flight_001",
      "carrier_code": "Carrier Code",
      "carrier_name": "Airline Name",
      "flight_number": "Flight Number",
      "origin": "Origin",
      "destination": "Destination",
      "departure_time": "Dep Time(HH:MM)",
      "arrival_time": "Arr Time(HH:MM)",
      "departure_date": "Dep Date(YYYY-MM-DD)",
      "duration": "Duration",
      "price": Price Number (controlled within {max_flight_price}),
      "cabin_class": "Economy",
      "stops": 0,
      "aircraft": "Aircraft Type",
      "available_seats": Available Seats
    }}
  ]
}}
```

Requirements:
1. Recommend 5 flight options.
2. Price must be between ¥200-¥{max_flight_price}.
3. Prioritize direct flights and Economy Class.
4. JSON format must be strictly followed.
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")

            # ✅ Extract JSON data
            flights_data = self._extract_json_from_response(content, "flights")

            if flights_data:
                # ✅ Filter overpriced flights
                filtered_flights = [
                    flight for flight in flights_data
                    if 200 <= flight.get('price', 0) <= max_flight_price * 1.2
                ]

                if not filtered_flights:
                    filtered_flights = self._adjust_flight_prices(flights_data, max_flight_price)

                print(f"✅ Successfully extracted {len(filtered_flights)} flight data entries (prices filtered)")

                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON Data】", "").replace("【Text Introduction】", "").strip()

                return {
                    "action": "search_flights",
                    "content": text_part + f"\n\n💡 **Budget Tip**: Suggested flight budget is ¥{max_flight_price}. We selected high-value options for you.",
                    "data": filtered_flights,
                    "suggestions": [
                        "Check return flights",
                        "Check baggage policy",
                        "Select seats"
                    ]
                }
            else:
                print("⚠️ Failed to extract JSON data, using fallback")
                return {
                    "action": "search_flights",
                    "content": content + "\n\n⚠️ Failed to get structured data",
                    "data": self._generate_smart_mock_flights(preferences, max_flight_price),
                    "suggestions": ["Search again"]
                }
        else:
            return self._generate_fallback_response("flight", context, preferences)

    # ✅ New: Adjust hotel prices to reasonable range
    def _adjust_hotel_prices(self, hotels: List[Dict], max_price: int) -> List[Dict]:
        """Adjust hotel prices to reasonable range"""
        adjusted = []
        for hotel in hotels:
            adjusted_hotel = hotel.copy()
            current_price = hotel.get('price', 500)

            if current_price > max_price:
                # Lower to 80% of max price
                adjusted_hotel['price'] = int(max_price * 0.8)
            elif current_price < 100:
                # Raise to at least 100
                adjusted_hotel['price'] = 100

            adjusted.append(adjusted_hotel)

        return adjusted

    # ✅ New: Adjust flight prices to reasonable range
    def _adjust_flight_prices(self, flights: List[Dict], max_price: int) -> List[Dict]:
        """Adjust flight prices to reasonable range"""
        adjusted = []
        for flight in flights:
            adjusted_flight = flight.copy()
            current_price = flight.get('price', 800)

            if current_price > max_price:
                adjusted_flight['price'] = int(max_price * 0.8)
            elif current_price < 200:
                adjusted_flight['price'] = 200

            adjusted.append(adjusted_flight)

        return adjusted

    # ✅ Improved Smart Mock Data Generation
    def _generate_smart_mock_hotels(self, preferences: Dict, max_price: int) -> List[Dict]:
        """Generate smart-priced mock hotel data"""
        print(f"⚠️ Generating smart fallback hotel data (Max Price: ¥{max_price})")

        destination = preferences.get("destination", "Destination") if preferences else "Destination"

        # Generate 3 hotels with different price points
        price_ranges = [
            int(max_price * 0.3),  # Low price
            int(max_price * 0.6),  # Mid price
            int(max_price * 0.9)   # High price
        ]

        hotels = []
        hotel_templates = [
            {"name": f"{destination} Economy Chain Hotel", "type": "Economy", "rating": 3.8},
            {"name": f"{destination} Business Select Hotel", "type": "Business", "rating": 4.2},
            {"name": f"{destination} Quality Living Hotel", "type": "Comfort", "rating": 4.5}
        ]

        for idx, (template, price) in enumerate(zip(hotel_templates, price_ranges)):
            hotels.append({
                "id": f"hotel_{idx+1:03d}",
                "name": template["name"],
                "location": f"{destination} Downtown",
                "address": f"{destination} City XX Road No.{100+idx*50}",
                "tel": f"400-{1000+idx:04d}-{5000+idx:04d}",
                "price": price,
                "rating": template["rating"],
                "amenities": ["Free WiFi", "24h Front Desk", "A/C"] if idx == 0 else
                             ["Free WiFi", "Gym", "Business Center", "Parking"] if idx == 1 else
                             ["Free WiFi", "Gym", "Pool", "Business Center", "Parking", "Breakfast"],
                "landmark": f"Located {0.3+idx*0.2:.1f} km from Subway Station",
                "description": f"{template['type']}, high value-for-money"
            })

        return hotels

    def _generate_smart_mock_flights(self, preferences: Dict, max_price: int) -> List[Dict]:
        """Generate smart-priced mock flight data"""
        print(f"⚠️ Generating smart fallback flight data (Max Price: ¥{max_price})")

        origin = preferences.get("origin", "Beijing") if preferences else "Beijing"
        destination = preferences.get("destination", "Shanghai") if preferences else "Shanghai"

        # Generate 3 flights with different price points
        price_ranges = [
            int(max_price * 0.4),  # Low price
            int(max_price * 0.7),  # Mid price
            int(max_price * 0.95)  # High price
        ]

        airlines = [
            {"code": "MU", "name": "China Eastern"},
            {"code": "CA", "name": "Air China"},
            {"code": "CZ", "name": "China Southern"}
        ]

        flights = []
        departure_times = ["08:30", "13:45", "18:20"]

        for idx, (airline, price, dep_time) in enumerate(zip(airlines, price_ranges, departure_times)):
            # Calculate arrival time (assuming 2.5 hours flight)
            dep_hour, dep_min = map(int, dep_time.split(':'))
            arr_hour = (dep_hour + 2) % 24
            arr_min = (dep_min + 30) % 60

            flights.append({
                "id": f"flight_{idx+1:03d}",
                "carrier_code": airline["code"],
                "carrier_name": airline["name"],
                "flight_number": f"{airline['code']}{1234+idx}",
                "origin": origin,
                "destination": destination,
                "departure_time": dep_time,
                "arrival_time": f"{arr_hour:02d}:{arr_min:02d}",
                "departure_date": str((datetime.now() + timedelta(days=1)).date()),
                "duration": "2 hours 30 minutes",
                "price": price,
                "cabin_class": "Economy Class",
                "stops": 0,
                "aircraft": "Boeing 737" if idx == 0 else "Airbus A320" if idx == 1 else "Boeing 787",
                "available_seats": 20 + idx * 5
            })

        return flights

    # Continue with other original methods...
    def _handle_full_planning(self, context: str, preferences: Dict) -> Dict:
        """Handle full itinerary planning"""
        prompt = f"""
You are a professional travel planner. User Request: {context}

Please formulate a detailed travel plan for the user, including:
1. Daily itinerary (morning, afternoon, evening)
2. Attraction recommendations and visit suggestions
3. Dining recommendations
4. Transportation advice
5. Important notes

Please use clear, friendly language, and return in markdown format.
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            return {
                "action": "full_planning",
                "content": content,
                "data": self._extract_planning_data(content),
                "suggestions": [
                    "View hotel recommendations",
                    "Check flight information",
                    "Check local weather"
                ]
            }
        else:
            return {
                "action": "full_planning",
                "content": self._generate_fallback_planning(context, preferences),
                "data": None,
                "suggestions": ["Regenerate", "Modify request"]
            }

    def _handle_weather_query(self, context: str, preferences: Dict) -> Dict:
        """Handle weather query"""
        prompt = f"""
You are a professional weather assistant. User Request: {context}

Please provide weather information and return in the following JSON format:

【Text Description】
(Write weather overview and suggestions here)

【JSON Data】
```json
{{
  "city": "City Name",
  "location": "Location Name",
  "temperature": Temperature Number,
  "feels_like": Feels Like Temperature,
  "weather": "Weather Condition",
  "description": "Weather Description",
  "humidity": Humidity,
  "wind_speed": "Wind Speed",
  "wind_direction": "Wind Direction",
  "forecast": [
    {{
      "date": "Date",
      "temp_high": High Temp,
      "temp_low": Low Temp,
      "weather": "Weather",
      "description": "Description"
    }}
  ]
}}
```
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            weather_data = self._extract_json_from_response(content, "city", is_dict=True)

            if weather_data:
                text_part = content.split("```json")[0].strip()
                return {
                    "action": "weather",
                    "content": text_part,
                    "data": weather_data,
                    "suggestions": [
                        "View next week's weather",
                        "Check clothing suggestions",
                        "View sunrise/sunset"
                    ]
                }
            else:
                return {
                    "action": "weather",
                    "content": content,
                    "data": self._generate_mock_weather(preferences),
                    "suggestions": ["Query again"]
                }
        else:
            return self._generate_fallback_response("weather", context, preferences)

    def _handle_attraction_query(self, context: str, preferences: Dict) -> Dict:
        """Handle attraction query"""
        prompt = f"""
You are a professional travel consultant. User Request: {context}

Please recommend attractions and provide detailed visit suggestions. Include:
1. Attraction name and features
2. Opening hours and ticket prices
3. Visit suggestions and notes
4. Transportation guidance

Please return in markdown format.
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            return {
                "action": "attraction",
                "content": content,
                "data": None,
                "suggestions": [
                    "View nearby hotels",
                    "Check local cuisine",
                    "View transportation routes"
                ]
            }
        else:
            return {
                "action": "attraction",
                "content": "Searching for attraction information...",
                "data": None,
                "suggestions": ["Retry", "Change destination"]
            }

    def _handle_general_query(self, context: str, preferences: Dict) -> Dict:
        """Handle general queries"""
        prompt = f"""
You are a friendly travel assistant. User Question: {context}

Please answer the user's question with concise, friendly language.
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            return {
                "action": "general",
                "content": content,
                "data": None,
                "suggestions": self._generate_suggestions(context)
            }
        else:
            return {
                "action": "general",
                "content": "Sorry, AI service is temporarily unavailable. Please try again later or attempt a more specific question.",
                "data": None,
                "suggestions": ["Ask again", "View help", "Contact support"]
            }

    def _extract_json_from_response(self, content: str, key: str, is_dict: bool = False) -> Any:
        """Extract JSON data from AI response"""
        try:
            # Method 1: Extract ```json``` code block
            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content, re.MULTILINE)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)

                if is_dict:
                    return data if key in str(data) else None
                else:
                    return data.get(key, [])

            # Method 2: Find the first complete JSON object
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                if is_dict:
                    return data
                else:
                    return data.get(key, [])

        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing failed: {e}")
        except Exception as e:
            print(f"❌ Failed to extract JSON: {e}")

        return None if is_dict else []

    def _call_deepseek_api(self, prompt: str, max_retries: int = 3) -> Dict:
        """Call DeepSeek API"""
        print("🚀 Calling DeepSeek API...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a professional, friendly travel assistant. You give reasonable advice based on user budget and avoid recommending overly expensive options."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }

        for attempt in range(max_retries):
            try:
                print(f"📡 Attempt {attempt + 1}/{max_retries}...")

                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    print(f"✅ API response success, length: {len(content)} chars")
                    return {"content": content}
                elif response.status_code == 429:
                    print(f"⚠️ API rate limit exceeded, waiting to retry...")
                    wait_time = 5 * (attempt + 1)
                    time.sleep(wait_time)
                elif response.status_code == 401:
                    print(f"❌ Invalid API key")
                    return {"error": "Invalid API key"}
                else:
                    print(f"❌ API error: {response.status_code} - {response.text[:200]}")
                    if attempt < max_retries - 1:
                        print("Waiting to retry...")
                        time.sleep(3)

            except requests.exceptions.Timeout:
                print(f"⚠️ Request timeout (Attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print("Waiting to retry...")
                    time.sleep(3)

            except requests.exceptions.ConnectionError as e:
                print(f"⚠️ Connection error: {e}")
                if attempt < max_retries - 1:
                    print("Waiting to retry...")
                    time.sleep(3)

            except Exception as e:
                print(f"❌ Failed to call DeepSeek API: {e}")
                break

        print("❌ All retries failed")
        return {"error": "API call failed, please check network connection or try again later"}

    # ==================== Fallback Generation Functions ====================

    def _generate_fallback_planning(self, context: str, preferences: Dict) -> str:
        """Generate backup itinerary planning"""
        destination = preferences.get("destination", "Destination") if preferences else "Destination"
        days = preferences.get("days", 3) if preferences else 3
        budget = preferences.get("budget", 5000) if preferences else 5000

        return f"""
🗺️ **{destination} Travel Plan**

Although the AI service is temporarily unavailable, I have prepared a reference itinerary framework for you:

📅 **Itinerary Overview**
- Destination: {destination}
- Days: {days} days
- Budget: ¥{budget}

🌟 **Day 1 - Arrival & First Look**
• Morning: Arrive in {destination}, check into hotel
• Afternoon: Visit city center landmarks
• Evening: Taste local specialty cuisine

🌟 **Day 2 - Deep Exploration** • Morning: Visit famous cultural attractions
• Afternoon: Experience local specialty activities
• Evening: Visit night market or shopping street

🌟 **Day 3 - Free Exploration** • Morning: Free activity or supplementary visit
• Afternoon: Shopping and prepare for return
• Evening: Return trip

💡 **Friendly Reminder**
1. Recommended to book hotels and tickets in advance
2. Have necessary travel documents ready
3. Check local weather, prepare appropriate clothing
4. Download offline maps just in case

📄 You can click "Regenerate" to get a more detailed AI-customized itinerary.
"""

    def _generate_fallback_response(self, type: str, context: str, preferences: Dict) -> Dict:
        """Generate fallback response"""
        fallback_messages = {
            "hotel": "Searching for suitable hotels, please wait...",
            "flight": "Checking flight information, please wait...",
            "weather": "Fetching weather information, please wait...",
            "attraction": "Searching for attraction information, please wait...",
            "general": "Processing your request, please wait..."
        }

        return {
            "action": type,
            "content": fallback_messages.get(type, "Processing..."),
            "data": None,
            "suggestions": ["Retry", "Ask another question", "View help"]
        }

    def _extract_planning_data(self, content: str) -> Dict:
        """Extract structured data from AI-generated content"""
        data = {
            "destination": "",
            "days": 0,
            "budget": 0,
            "itinerary": {}
        }

        # Note: This regex looks for "X days" or "X天" (if mixed). 
        # Since we translated the output to English, it will likely be "X days".
        if "day" in content.lower():
            import re
            # Search for pattern like "3 days" or "3 day"
            days_match = re.search(r'(\d+)\s*day', content.lower())
            if days_match:
                data["days"] = int(days_match.group(1))

        return data if any(data.values()) else None

    def _generate_suggestions(self, context: str) -> List[str]:
        """Generate relevant suggestions"""
        suggestions = []

        if "hotel" in context.lower() or "stay" in context.lower():
            suggestions.extend(["View more hotels", "Check hotel location", "View user reviews"])
        elif "flight" in context.lower() or "ticket" in context.lower():
            suggestions.extend(["Check return flights", "Baggage policy", "Select seats"])
        elif "weather" in context.lower():
            suggestions.extend(["View next week's weather", "Clothing suggestions", "View sunrise/sunset"])
        else:
            suggestions.extend(["Tell me more needs", "View popular recommendations", "Start planning"])

        return suggestions[:3]

    def _generate_mock_weather(self, preferences: Dict) -> Dict:
        """Generate mock weather data"""
        print("⚠️ Using fallback weather data")
        destination = preferences.get("destination", "Example City") if preferences else "Example City"

        return {
            "city": destination,
            "location": destination,
            "temperature": 20,
            "feels_like": 18,
            "weather": "Sunny",
            "description": "Sunny",
            "humidity": 60,
            "wind_speed": "3.0 m/s",
            "forecast": [
                {"date": "Tomorrow", "temp_high": 22, "temp_low": 16, "weather": "Sunny", "description": "Sunny"},
                {"date": "Day after tomorrow", "temp_high": 23, "temp_low": 17, "weather": "Cloudy", "description": "Cloudy"}
            ]
        }


# Export Agent class
__all__ = ['TravelAgent']