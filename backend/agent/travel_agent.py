"""
TripPilot Travel Agent - Improved Version with Multilingual Support
New Features:
1. 🎯 Intelligent Budget Allocation
2. 💰 Price Reasonableness Check
3. 📊 Dynamic Recommendation Adjustment based on Remaining Budget
4. ✅ Ensure recommended prices do not exhaust the entire budget
5. 🌍 Automatic Language Detection and Response (NEW)
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
        self.current_language = 'en'  # 默认语言

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

    # ✅ NEW: Detect user language
    def _detect_language(self, text: str) -> str:
        """
        Detect text language

        Args:
            text: Text to detect

        Returns:
            'zh' for Chinese, 'en' for English
        """
        # Check if text contains Chinese characters
        if re.search(r'[\u4e00-\u9fff]', text):
            return 'zh'
        return 'en'

    # ✅ Calculate Reasonable Budget Allocation
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

        # ✅ NEW: Detect user language
        self.current_language = self._detect_language(message)
        print(f"🌍 Detected Language: {self.current_language}")

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
            # Add remaining budget info
            if preferences.get("remaining_budget") is not None:
                context_parts.append(f"Remaining Budget: ¥{preferences['remaining_budget']}")
            if preferences.get("start_date") and preferences.get("end_date"):
                context_parts.append(f"Dates: {preferences['start_date']} to {preferences['end_date']}")

        return " | ".join(context_parts)

    def _identify_intent(self, message: str) -> str:
        """Identify user intent"""
        message_lower = message.lower()

        # Keywords to recognize both English and Chinese input
        intent_keywords = {
            "full_planning": [
                # English
                "plan", "itinerary", "arrange", "schedule", "play", "trip", "travel", "tour", "day trip",
                # Chinese
                "计划", "行程", "安排", "规划", "玩", "旅游", "旅行", "游玩"
            ],
            "search_hotels": [
                # English
                "hotel", "accommodation", "inn", "hostel", "stay", "lodging",
                # Chinese
                "酒店", "住宿", "宾馆", "旅馆", "民宿"
            ],
            "search_flights": [
                # English
                "flight", "ticket", "plane", "fly", "airline",
                # Chinese
                "机票", "航班", "飞机", "航空"
            ],
            "weather": [
                # English
                "weather", "temperature", "rain", "temp", "wear", "forecast",
                # Chinese
                "天气", "气温", "温度", "下雨", "穿衣", "预报"
            ],
            "attraction": [
                # English
                "attraction", "sightseeing", "where to go", "recommend", "must-see", "visit",
                # Chinese
                "景点", "游玩", "去哪", "推荐", "必去", "参观"
            ]
        }

        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "general"

    def _handle_hotel_search(self, context: str, preferences: Dict) -> Dict:
        """Handle hotel search - with smart budget control"""

        # Get budget information
        total_budget = preferences.get("budget", 5000) if preferences else 5000
        remaining_budget = preferences.get("remaining_budget", total_budget) if preferences else total_budget
        days = preferences.get("days", 3) if preferences else 3

        # Calculate reasonable hotel price range
        budget_allocation = self._calculate_budget_allocation(total_budget, remaining_budget, days)
        max_hotel_price = int(budget_allocation["hotel_per_night_max"])

        # Ensure reasonable price (min 100, max not exceeding 40% of remaining budget)
        max_hotel_price = max(100, min(max_hotel_price, int(remaining_budget * 0.4)))

        # Create prompt based on language
        if self.current_language == 'zh':
            prompt = f"""
你是专业的酒店推荐助手。用户请求：{context}

🎯 重要预算信息：
- 用户总预算：¥{total_budget}
- 剩余预算：¥{remaining_budget}
- 旅行天数：{days}天
- 建议每晚酒店预算：¥{max_hotel_price}以内

⚠️ 请注意：
1. 推荐的酒店价格不能太高，要给用餐和娱乐留够预算
2. 价格应控制在¥100 - ¥{max_hotel_price}/晚
3. 推荐高性价比的选择，不是越贵越好

请按以下格式返回，先用自然语言介绍，再提供JSON数据：

【文字介绍】
(在这里写推荐理由和说明，解释为什么这些酒店性价比高)

【JSON数据】
```json
{{
  "hotels": [
    {{
      "id": "hotel_001",
      "name": "酒店名称",
      "location": "位置",
      "address": "详细地址",
      "tel": "电话",
      "price": 价格数字(控制在{max_hotel_price}以内),
      "rating": 评分数字,
      "amenities": ["设施1", "设施2"],
      "landmark": "地标描述",
      "description": "简短描述"
    }}
  ]
}}
```

要求：
1. 推荐5家真实存在的酒店
2. 价格必须在¥100-¥{max_hotel_price}之间，考虑用户剩余预算
3. 优先推荐高性价比的中档酒店
4. JSON格式必须严格正确，无语法错误
5. 每个字段必须完整填写
"""
        else:
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

            # Extract JSON data
            hotels_data = self._extract_json_from_response(content, "hotels")

            if hotels_data:
                # Filter overpriced hotels
                filtered_hotels = [
                    hotel for hotel in hotels_data
                    if 100 <= hotel.get('price', 0) <= max_hotel_price * 1.2  # Allow 20% buffer
                ]

                # If no hotels left after filtering, use original data but reduce price
                if not filtered_hotels:
                    filtered_hotels = self._adjust_hotel_prices(hotels_data, max_hotel_price)

                print(f"✅ Successfully extracted {len(filtered_hotels)} hotel data entries (prices filtered)")

                # Extract text part (content before JSON)
                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON数据】", "").replace("【文字介绍】", "").strip()
                text_part = text_part.replace("【JSON Data】", "").replace("【Text Introduction】", "").strip()

                # Add budget tip based on language
                budget_tip = f"\n\n💡 **预算提示**：建议每晚酒店预算为¥{max_hotel_price}。我们为您挑选了高性价比的选择。" if self.current_language == 'zh' else f"\n\n💡 **Budget Tip**: Suggested hotel budget per night is ¥{max_hotel_price}. We selected high-value options for you."

                return {
                    "action": "search_hotels",
                    "content": text_part + budget_tip,
                    "data": filtered_hotels,
                    "suggestions": [
                        "查看更多酒店" if self.current_language == 'zh' else "View more hotels",
                        "调整价格范围" if self.current_language == 'zh' else "Adjust price range",
                        "查看用户评价" if self.current_language == 'zh' else "View user reviews"
                    ]
                }
            else:
                # If extraction fails, return text but give warning
                print("⚠️ Failed to extract JSON data, using fallback")
                warning = "\n\n⚠️ 未能获取结构化数据，请尝试重新搜索。" if self.current_language == 'zh' else "\n\n⚠️ Failed to get structured data, please try searching again."

                return {
                    "action": "search_hotels",
                    "content": content + warning,
                    "data": self._generate_smart_mock_hotels(preferences, max_hotel_price),
                    "suggestions": ["重新搜索" if self.current_language == 'zh' else "Search again",
                                   "更改条件" if self.current_language == 'zh' else "Change criteria"]
                }
        else:
            return self._generate_fallback_response("hotel", context, preferences)

    def _handle_flight_search(self, context: str, preferences: Dict) -> Dict:
        """Handle flight search - with smart budget control"""

        # Get budget information
        total_budget = preferences.get("budget", 5000) if preferences else 5000
        remaining_budget = preferences.get("remaining_budget", total_budget) if preferences else total_budget
        days = preferences.get("days", 3) if preferences else 3

        # Calculate reasonable flight price range
        budget_allocation = self._calculate_budget_allocation(total_budget, remaining_budget, days)
        max_flight_price = int(budget_allocation["flight_max"])

        # Ensure reasonable price (min 200, max not exceeding 50% of remaining budget)
        max_flight_price = max(200, min(max_flight_price, int(remaining_budget * 0.5)))

        if self.current_language == 'zh':
            prompt = f"""
你是专业的航班搜索助手。用户请求：{context}

🎯 重要预算信息：
- 用户总预算：¥{total_budget}
- 剩余预算：¥{remaining_budget}
- 建议机票预算：¥{max_flight_price}以内

⚠️ 请注意：
1. 推荐的机票价格必须合理，不能把所有预算花在机票上
2. 价格应控制在¥200 - ¥{max_flight_price}
3. 优先推荐经济舱，商务舱和头等舱太贵

请按以下格式返回：

【文字介绍】
(在这里写航班推荐说明，强调性价比)

【JSON数据】
```json
{{
  "flights": [
    {{
      "id": "flight_001",
      "carrier_code": "航司代码",
      "carrier_name": "航空公司名称",
      "flight_number": "航班号",
      "origin": "出发地",
      "destination": "目的地",
      "departure_time": "起飞时间(HH:MM)",
      "arrival_time": "到达时间(HH:MM)",
      "departure_date": "起飞日期(YYYY-MM-DD)",
      "duration": "飞行时长",
      "price": 价格数字(控制在{max_flight_price}以内),
      "cabin_class": "经济舱",
      "stops": 0,
      "aircraft": "机型",
      "available_seats": 可用座位数
    }}
  ]
}}
```

要求：
1. 推荐5个航班选择
2. 价格必须在¥200-¥{max_flight_price}之间
3. 优先推荐直飞和经济舱
4. JSON格式必须严格正确
"""
        else:
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

            # Extract JSON data
            flights_data = self._extract_json_from_response(content, "flights")

            if flights_data:
                # Filter overpriced flights
                filtered_flights = [
                    flight for flight in flights_data
                    if 200 <= flight.get('price', 0) <= max_flight_price * 1.2
                ]

                if not filtered_flights:
                    filtered_flights = self._adjust_flight_prices(flights_data, max_flight_price)

                print(f"✅ Successfully extracted {len(filtered_flights)} flight data entries (prices filtered)")

                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON数据】", "").replace("【文字介绍】", "").strip()
                text_part = text_part.replace("【JSON Data】", "").replace("【Text Introduction】", "").strip()

                budget_tip = f"\n\n💡 **预算提示**：建议机票预算为¥{max_flight_price}。我们为您挑选了高性价比的选择。" if self.current_language == 'zh' else f"\n\n💡 **Budget Tip**: Suggested flight budget is ¥{max_flight_price}. We selected high-value options for you."

                return {
                    "action": "search_flights",
                    "content": text_part + budget_tip,
                    "data": filtered_flights,
                    "suggestions": [
                        "查看返程航班" if self.current_language == 'zh' else "Check return flights",
                        "查看行李政策" if self.current_language == 'zh' else "Check baggage policy",
                        "选择座位" if self.current_language == 'zh' else "Select seats"
                    ]
                }
            else:
                print("⚠️ Failed to extract JSON data, using fallback")
                warning = "\n\n⚠️ 未能获取结构化数据" if self.current_language == 'zh' else "\n\n⚠️ Failed to get structured data"

                return {
                    "action": "search_flights",
                    "content": content + warning,
                    "data": self._generate_smart_mock_flights(preferences, max_flight_price),
                    "suggestions": ["重新搜索" if self.current_language == 'zh' else "Search again"]
                }
        else:
            return self._generate_fallback_response("flight", context, preferences)

    # Adjust hotel prices to reasonable range
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

    # Adjust flight prices to reasonable range
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

    # Improved Smart Mock Data Generation
    def _generate_smart_mock_hotels(self, preferences: Dict, max_price: int) -> List[Dict]:
        """Generate smart-priced mock hotel data"""
        print(f"⚠️ Generating smart fallback hotel data (Max Price: ¥{max_price})")

        destination = preferences.get("destination", "目的地" if self.current_language == 'zh' else "Destination") if preferences else ("目的地" if self.current_language == 'zh' else "Destination")

        # Generate 3 hotels with different price points
        price_ranges = [
            int(max_price * 0.3),  # Low price
            int(max_price * 0.6),  # Mid price
            int(max_price * 0.9)   # High price
        ]

        hotels = []
        if self.current_language == 'zh':
            hotel_templates = [
                {"name": f"{destination}经济连锁酒店", "type": "经济型", "rating": 3.8},
                {"name": f"{destination}商务精选酒店", "type": "商务型", "rating": 4.2},
                {"name": f"{destination}品质生活酒店", "type": "舒适型", "rating": 4.5}
            ]
            amenities_list = [
                ["免费WiFi", "24小时前台", "空调"],
                ["免费WiFi", "健身房", "商务中心", "停车场"],
                ["免费WiFi", "健身房", "游泳池", "商务中心", "停车场", "早餐"]
            ]
        else:
            hotel_templates = [
                {"name": f"{destination} Economy Chain Hotel", "type": "Economy", "rating": 3.8},
                {"name": f"{destination} Business Select Hotel", "type": "Business", "rating": 4.2},
                {"name": f"{destination} Quality Living Hotel", "type": "Comfort", "rating": 4.5}
            ]
            amenities_list = [
                ["Free WiFi", "24h Front Desk", "A/C"],
                ["Free WiFi", "Gym", "Business Center", "Parking"],
                ["Free WiFi", "Gym", "Pool", "Business Center", "Parking", "Breakfast"]
            ]

        for idx, (template, price) in enumerate(zip(hotel_templates, price_ranges)):
            location_text = f"距地铁站{0.3+idx*0.2:.1f}公里" if self.current_language == 'zh' else f"Located {0.3+idx*0.2:.1f} km from Subway Station"
            desc_text = f"{template['type']}，高性价比" if self.current_language == 'zh' else f"{template['type']}, high value-for-money"

            hotels.append({
                "id": f"hotel_{idx+1:03d}",
                "name": template["name"],
                "location": f"{destination}市中心" if self.current_language == 'zh' else f"{destination} Downtown",
                "address": f"{destination}市XX路{100+idx*50}号" if self.current_language == 'zh' else f"{destination} City XX Road No.{100+idx*50}",
                "tel": f"400-{1000+idx:04d}-{5000+idx:04d}",
                "price": price,
                "rating": template["rating"],
                "amenities": amenities_list[idx],
                "landmark": location_text,
                "description": desc_text
            })

        return hotels

    def _generate_smart_mock_flights(self, preferences: Dict, max_price: int) -> List[Dict]:
        """Generate smart-priced mock flight data"""
        print(f"⚠️ Generating smart fallback flight data (Max Price: ¥{max_price})")

        origin = preferences.get("origin", "北京" if self.current_language == 'zh' else "Beijing") if preferences else ("北京" if self.current_language == 'zh' else "Beijing")
        destination = preferences.get("destination", "上海" if self.current_language == 'zh' else "Shanghai") if preferences else ("上海" if self.current_language == 'zh' else "Shanghai")

        # Generate 3 flights with different price points
        price_ranges = [
            int(max_price * 0.4),  # Low price
            int(max_price * 0.7),  # Mid price
            int(max_price * 0.95)  # High price
        ]

        airlines = [
            {"code": "MU", "name": "东方航空" if self.current_language == 'zh' else "China Eastern"},
            {"code": "CA", "name": "国航" if self.current_language == 'zh' else "Air China"},
            {"code": "CZ", "name": "南方航空" if self.current_language == 'zh' else "China Southern"}
        ]

        flights = []
        departure_times = ["08:30", "13:45", "18:20"]

        for idx, (airline, price, dep_time) in enumerate(zip(airlines, price_ranges, departure_times)):
            # Calculate arrival time (assuming 2.5 hours flight)
            dep_hour, dep_min = map(int, dep_time.split(':'))
            arr_hour = (dep_hour + 2) % 24
            arr_min = (dep_min + 30) % 60

            duration_text = "2小时30分钟" if self.current_language == 'zh' else "2 hours 30 minutes"
            cabin_text = "经济舱" if self.current_language == 'zh' else "Economy Class"

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
                "duration": duration_text,
                "price": price,
                "cabin_class": cabin_text,
                "stops": 0,
                "aircraft": "Boeing 737" if idx == 0 else "Airbus A320" if idx == 1 else "Boeing 787",
                "available_seats": 20 + idx * 5
            })

        return flights

    # Continue with other original methods...
    def _handle_full_planning(self, context: str, preferences: Dict) -> Dict:
        """Handle full itinerary planning"""

        if self.current_language == 'zh':
            prompt = f"""
你是专业的旅游规划师。用户请求：{context}

请为用户制定详细的旅游计划，包括：
1. 每日行程安排（上午、下午、晚上）
2. 景点推荐和游玩建议
3. 餐饮推荐
4. 交通建议
5. 注意事项

请用清晰、友好的语言，以markdown格式返回。
"""
        else:
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
            suggestions = [
                "查看酒店推荐" if self.current_language == 'zh' else "View hotel recommendations",
                "查看航班信息" if self.current_language == 'zh' else "Check flight information",
                "查看当地天气" if self.current_language == 'zh' else "Check local weather"
            ]
            return {
                "action": "full_planning",
                "content": content,
                "data": self._extract_planning_data(content),
                "suggestions": suggestions
            }
        else:
            suggestions = [
                "重新生成" if self.current_language == 'zh' else "Regenerate",
                "修改需求" if self.current_language == 'zh' else "Modify request"
            ]
            return {
                "action": "full_planning",
                "content": self._generate_fallback_planning(context, preferences),
                "data": None,
                "suggestions": suggestions
            }

    def _handle_weather_query(self, context: str, preferences: Dict) -> Dict:
        """Handle weather query"""

        if self.current_language == 'zh':
            prompt = f"""
你是专业的天气助手。用户请求：{context}

请提供天气信息，并按以下JSON格式返回：

【文字描述】
(在这里写天气概况和建议)

【JSON数据】
```json
{{
  "city": "城市名称",
  "location": "位置名称",
  "temperature": 温度数字,
  "feels_like": 体感温度,
  "weather": "天气状况",
  "description": "天气描述",
  "humidity": 湿度,
  "wind_speed": "风速",
  "wind_direction": "风向",
  "forecast": [
    {{
      "date": "日期",
      "temp_high": 最高温,
      "temp_low": 最低温,
      "weather": "天气",
      "description": "描述"
    }}
  ]
}}
```
"""
        else:
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
                text_part = text_part.replace("【JSON数据】", "").replace("【文字描述】", "").strip()
                text_part = text_part.replace("【JSON Data】", "").replace("【Text Description】", "").strip()

                suggestions = [
                    "查看下周天气" if self.current_language == 'zh' else "View next week's weather",
                    "查看穿衣建议" if self.current_language == 'zh' else "Check clothing suggestions",
                    "查看日出日落" if self.current_language == 'zh' else "View sunrise/sunset"
                ]

                return {
                    "action": "weather",
                    "content": text_part,
                    "data": weather_data,
                    "suggestions": suggestions
                }
            else:
                return {
                    "action": "weather",
                    "content": content,
                    "data": self._generate_mock_weather(preferences),
                    "suggestions": ["重新查询" if self.current_language == 'zh' else "Query again"]
                }
        else:
            return self._generate_fallback_response("weather", context, preferences)

    def _handle_attraction_query(self, context: str, preferences: Dict) -> Dict:
        """Handle attraction query"""

        if self.current_language == 'zh':
            prompt = f"""
你是专业的旅游顾问。用户请求：{context}

请推荐景点并提供详细的游玩建议。包括：
1. 景点名称和特色
2. 开放时间和门票价格
3. 游玩建议和注意事项
4. 交通指引

请以markdown格式返回。
"""
        else:
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
            suggestions = [
                "查看附近酒店" if self.current_language == 'zh' else "View nearby hotels",
                "查看当地美食" if self.current_language == 'zh' else "Check local cuisine",
                "查看交通路线" if self.current_language == 'zh' else "View transportation routes"
            ]
            return {
                "action": "attraction",
                "content": content,
                "data": None,
                "suggestions": suggestions
            }
        else:
            suggestions = [
                "重试" if self.current_language == 'zh' else "Retry",
                "更换目的地" if self.current_language == 'zh' else "Change destination"
            ]
            return {
                "action": "attraction",
                "content": "正在搜索景点信息..." if self.current_language == 'zh' else "Searching for attraction information...",
                "data": None,
                "suggestions": suggestions
            }

    def _handle_general_query(self, context: str, preferences: Dict) -> Dict:
        """Handle general queries"""

        if self.current_language == 'zh':
            prompt = f"""
你是友好的旅游助手。用户问题：{context}

请用简洁、友好的语言回答用户的问题。
"""
        else:
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
            error_msg = "抱歉，AI服务暂时不可用。请稍后重试或尝试更具体的问题。" if self.current_language == 'zh' else "Sorry, AI service is temporarily unavailable. Please try again later or attempt a more specific question."
            suggestions = [
                "再次询问" if self.current_language == 'zh' else "Ask again",
                "查看帮助" if self.current_language == 'zh' else "View help",
                "联系客服" if self.current_language == 'zh' else "Contact support"
            ]
            return {
                "action": "general",
                "content": error_msg,
                "data": None,
                "suggestions": suggestions
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
        """Call DeepSeek API with language awareness"""
        print("🚀 Calling DeepSeek API...")

        # ✅ Add language instruction prefix
        language_instructions = {
            'zh': "【重要】请用中文回复用户的所有问题和内容。\n\n",
            'en': "【IMPORTANT】Please reply to all user questions and content in English.\n\n"
        }

        system_messages = {
            'zh': "你是一个专业、友好的旅游助手。你会根据用户预算给出合理建议，避免推荐过于昂贵的选项。你必须用中文与用户交流。",
            'en': "You are a professional, friendly travel assistant. You give reasonable advice based on user budget and avoid recommending overly expensive options. You must communicate with users in English."
        }

        # Add language instruction to prompt
        final_prompt = language_instructions[self.current_language] + prompt

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_messages[self.current_language]},
                {"role": "user", "content": final_prompt}
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
        error_msg = "API调用失败，请检查网络连接或稍后重试" if self.current_language == 'zh' else "API call failed, please check network connection or try again later"
        return {"error": error_msg}

    # ==================== Fallback Generation Functions ====================

    def _generate_fallback_planning(self, context: str, preferences: Dict) -> str:
        """Generate backup itinerary planning"""
        destination = preferences.get("destination", "目的地" if self.current_language == 'zh' else "Destination") if preferences else ("目的地" if self.current_language == 'zh' else "Destination")
        days = preferences.get("days", 3) if preferences else 3
        budget = preferences.get("budget", 5000) if preferences else 5000

        if self.current_language == 'zh':
            return f"""
🗺️ **{destination}旅行计划**

虽然AI服务暂时不可用，但我为您准备了一个参考行程框架：

📅 **行程概览**
- 目的地：{destination}
- 天数：{days}天
- 预算：¥{budget}

🌟 **第1天 - 抵达与初探**
• 上午：抵达{destination}，办理酒店入住
• 下午：游览市中心地标
• 晚上：品尝当地特色美食

🌟 **第2天 - 深度探索**
• 上午：参观著名文化景点
• 下午：体验当地特色活动
• 晚上：逛夜市或购物街

🌟 **第3天 - 自由探索**
• 上午：自由活动或补充游览
• 下午：购物，准备返程
• 晚上：返程

💡 **友情提示**
1. 建议提前预订酒店和门票
2. 准备好必要的旅行证件
3. 查看当地天气，准备合适衣物
4. 下载离线地图以备不时之需

🔄 您可以点击"重新生成"获取更详细的AI定制行程。
"""
        else:
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

🌟 **Day 2 - Deep Exploration**
• Morning: Visit famous cultural attractions
• Afternoon: Experience local specialty activities
• Evening: Visit night market or shopping street

🌟 **Day 3 - Free Exploration**
• Morning: Free activity or supplementary visit
• Afternoon: Shopping and prepare for return
• Evening: Return trip

💡 **Friendly Reminder**
1. Recommended to book hotels and tickets in advance
2. Have necessary travel documents ready
3. Check local weather, prepare appropriate clothing
4. Download offline maps just in case

🔄 You can click "Regenerate" to get a more detailed AI-customized itinerary.
"""

    def _generate_fallback_response(self, type: str, context: str, preferences: Dict) -> Dict:
        """Generate fallback response"""

        if self.current_language == 'zh':
            fallback_messages = {
                "hotel": "正在搜索合适的酒店，请稍候...",
                "flight": "正在查询航班信息，请稍候...",
                "weather": "正在获取天气信息，请稍候...",
                "attraction": "正在搜索景点信息，请稍候...",
                "general": "正在处理您的请求，请稍候..."
            }
            suggestions = ["重试", "换个问题", "查看帮助"]
        else:
            fallback_messages = {
                "hotel": "Searching for suitable hotels, please wait...",
                "flight": "Checking flight information, please wait...",
                "weather": "Fetching weather information, please wait...",
                "attraction": "Searching for attraction information, please wait...",
                "general": "Processing your request, please wait..."
            }
            suggestions = ["Retry", "Ask another question", "View help"]

        return {
            "action": type,
            "content": fallback_messages.get(type, "处理中..." if self.current_language == 'zh' else "Processing..."),
            "data": None,
            "suggestions": suggestions
        }

    def _extract_planning_data(self, content: str) -> Dict:
        """Extract structured data from AI-generated content"""
        data = {
            "destination": "",
            "days": 0,
            "budget": 0,
            "itinerary": {}
        }

        # Search for day patterns in both languages
        days_patterns = [
            r'(\d+)\s*天',  # Chinese: X天
            r'(\d+)\s*day'   # English: X day(s)
        ]

        for pattern in days_patterns:
            days_match = re.search(pattern, content.lower())
            if days_match:
                data["days"] = int(days_match.group(1))
                break

        return data if any(data.values()) else None

    def _generate_suggestions(self, context: str) -> List[str]:
        """Generate relevant suggestions"""
        suggestions = []
        context_lower = context.lower()

        if self.current_language == 'zh':
            if any(keyword in context_lower for keyword in ["酒店", "住宿", "hotel", "stay"]):
                suggestions.extend(["查看更多酒店", "查看酒店位置", "查看用户评价"])
            elif any(keyword in context_lower for keyword in ["机票", "航班", "flight", "ticket"]):
                suggestions.extend(["查看返程航班", "行李政策", "选择座位"])
            elif any(keyword in context_lower for keyword in ["天气", "weather"]):
                suggestions.extend(["查看下周天气", "穿衣建议", "查看日出日落"])
            else:
                suggestions.extend(["告诉我更多需求", "查看热门推荐", "开始规划"])
        else:
            if any(keyword in context_lower for keyword in ["hotel", "stay", "accommodation"]):
                suggestions.extend(["View more hotels", "Check hotel location", "View user reviews"])
            elif any(keyword in context_lower for keyword in ["flight", "ticket"]):
                suggestions.extend(["Check return flights", "Baggage policy", "Select seats"])
            elif "weather" in context_lower:
                suggestions.extend(["View next week's weather", "Clothing suggestions", "View sunrise/sunset"])
            else:
                suggestions.extend(["Tell me more needs", "View popular recommendations", "Start planning"])

        return suggestions[:3]

    def _generate_mock_weather(self, preferences: Dict) -> Dict:
        """Generate mock weather data"""
        print("⚠️ Using fallback weather data")
        destination = preferences.get("destination", "示例城市" if self.current_language == 'zh' else "Example City") if preferences else ("示例城市" if self.current_language == 'zh' else "Example City")

        if self.current_language == 'zh':
            return {
                "city": destination,
                "location": destination,
                "temperature": 20,
                "feels_like": 18,
                "weather": "晴天",
                "description": "晴朗",
                "humidity": 60,
                "wind_speed": "3.0米/秒",
                "forecast": [
                    {"date": "明天", "temp_high": 22, "temp_low": 16, "weather": "晴", "description": "晴朗"},
                    {"date": "后天", "temp_high": 23, "temp_low": 17, "weather": "多云", "description": "多云"}
                ]
            }
        else:
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