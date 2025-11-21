"""
TripPilot Travel Agent - 改进版
新功能：
1. 🎯 智能预算分配
2. 💰 价格合理性检查
3. 📊 根据剩余预算动态调整推荐
4. ✅ 确保推荐的价格不会耗尽所有预算
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
    """智能旅行助手Agent"""

    def __init__(self):
        """初始化Agent"""
        print("🚀 初始化TripPilot Agent...")

        self.config = Config()
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_BASE_URL
        self.model = Config.DEEPSEEK_MODEL

        self.init_tools()
        self.conversation_history = []

        print("✅ Agent初始化完成！\n")

    def init_tools(self):
        """初始化工具"""
        tools_status = []

        if Config.GAODE_API_KEY:
            tools_status.append("  高德API: ✅ 已配置")
        else:
            tools_status.append("  高德API: ❌ 未配置")

        if self.api_key:
            tools_status.append("  DeepSeek: ✅ 已配置")
        else:
            tools_status.append("  DeepSeek: ❌ 未配置")

        for status in tools_status:
            print(status)

        print("✅ 工具初始化完成")

        if self.api_key:
            print(f"✅ DeepSeek API已配置")
            print(f"   Key前缀: {self.api_key[:12]}...")

    # ✅ 新增：计算合理的预算分配
    def _calculate_budget_allocation(self, total_budget: float, remaining_budget: float, days: int) -> Dict[str, float]:
        """
        计算合理的预算分配

        Args:
            total_budget: 总预算
            remaining_budget: 剩余预算
            days: 旅行天数

        Returns:
            预算分配建议 (交通、住宿、其他)
        """
        # 如果剩余预算很少，返回保守建议
        if remaining_budget < total_budget * 0.3:
            return {
                "flight_max": remaining_budget * 0.3,
                "hotel_per_night_max": (remaining_budget * 0.4) / max(days - 1, 1),
                "other": remaining_budget * 0.3
            }

        # 正常情况：40%交通，30%住宿，30%其他
        return {
            "flight_max": remaining_budget * 0.4,
            "hotel_per_night_max": (remaining_budget * 0.3) / max(days - 1, 1),
            "other": remaining_budget * 0.3
        }

    def process_message(self, message: str, preferences: Dict = None) -> Dict:
        """处理用户消息"""
        print("=" * 60)
        print(f"📥 收到用户消息: {message}")

        if preferences:
            context = self._build_context(message, preferences)
        else:
            context = message

        intent = self._identify_intent(message)
        print(f"🎯 识别意图: {intent}")

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
        """构建上下文信息"""
        context_parts = [message]

        if preferences:
            if preferences.get("destination"):
                context_parts.append(f"目的地: {preferences['destination']}")
            if preferences.get("budget"):
                context_parts.append(f"总预算: ¥{preferences['budget']}")
            # ✅ 添加剩余预算信息
            if preferences.get("remaining_budget") is not None:
                context_parts.append(f"剩余预算: ¥{preferences['remaining_budget']}")
            if preferences.get("start_date") and preferences.get("end_date"):
                context_parts.append(f"日期: {preferences['start_date']} 至 {preferences['end_date']}")

        return " | ".join(context_parts)

    def _identify_intent(self, message: str) -> str:
        """识别用户意图"""
        message_lower = message.lower()

        intent_keywords = {
            "full_planning": ["规划", "行程", "安排", "计划", "游玩", "旅行", "旅游", "几天", "日游"],
            "search_hotels": ["酒店", "住宿", "旅馆", "民宿", "住哪"],
            "search_flights": ["航班", "机票", "飞机", "飞往"],
            "weather": ["天气", "气温", "下雨", "温度", "穿什么"],
            "attraction": ["景点", "好玩", "去哪", "推荐", "必游", "有什么"]
        }

        for intent, keywords in intent_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                return intent

        return "general"

    def _handle_hotel_search(self, context: str, preferences: Dict) -> Dict:
        """处理酒店搜索 - 带智能预算控制"""

        # ✅ 获取预算信息
        total_budget = preferences.get("budget", 5000) if preferences else 5000
        remaining_budget = preferences.get("remaining_budget", total_budget) if preferences else total_budget
        days = preferences.get("days", 3) if preferences else 3

        # ✅ 计算合理的酒店价格范围
        budget_allocation = self._calculate_budget_allocation(total_budget, remaining_budget, days)
        max_hotel_price = int(budget_allocation["hotel_per_night_max"])

        # 确保价格合理（最低100，最高不超过剩余预算的40%）
        max_hotel_price = max(100, min(max_hotel_price, int(remaining_budget * 0.4)))

        # ✅ 修改prompt，要求DeepSeek返回价格合理的酒店
        prompt = f"""
你是专业的酒店推荐助手。用户需求：{context}

🎯 重要预算信息：
- 用户总预算：¥{total_budget}
- 剩余预算：¥{remaining_budget}
- 旅行天数：{days}天
- 建议每晚酒店预算：¥{max_hotel_price}以内

⚠️ 请注意：
1. 推荐的酒店价格不能太高，要给用户留出足够的餐饮和娱乐预算
2. 价格应该控制在 ¥100 - ¥{max_hotel_price}/晚
3. 要推荐性价比高的选择，不是越贵越好

请按以下格式返回，先用自然语言介绍，然后提供JSON数据：

【文字介绍】
（这里写推荐理由和说明，说明为什么这些酒店性价比高）

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
      "landmark": "地标说明",
      "description": "简短描述"
    }}
  ]
}}
```

要求：
1. 推荐5个真实存在的酒店
2. 价格必须在¥100-¥{max_hotel_price}之间，考虑用户的剩余预算
3. 优先推荐性价比高的中等价位酒店
4. JSON格式必须严格遵守，不要有语法错误
5. 每个字段都要填写完整
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")

            # ✅ 提取JSON数据
            hotels_data = self._extract_json_from_response(content, "hotels")

            if hotels_data:
                # ✅ 过滤价格过高的酒店
                filtered_hotels = [
                    hotel for hotel in hotels_data
                    if 100 <= hotel.get('price', 0) <= max_hotel_price * 1.2  # 允许20%浮动
                ]

                # 如果过滤后没有酒店，使用原始数据但降低价格
                if not filtered_hotels:
                    filtered_hotels = self._adjust_hotel_prices(hotels_data, max_hotel_price)

                print(f"✅ 成功提取到 {len(filtered_hotels)} 个酒店数据（已过滤价格）")

                # ✅ 提取文字部分（JSON之前的内容）
                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON数据】", "").replace("【文字介绍】", "").strip()

                return {
                    "action": "search_hotels",
                    "content": text_part + f"\n\n💡 **预算提示**: 建议每晚酒店预算为 ¥{max_hotel_price}，为您精选了性价比高的选择。",
                    "data": filtered_hotels,
                    "suggestions": [
                        "查看更多酒店",
                        "调整价格范围",
                        "查看用户评价"
                    ]
                }
            else:
                # ✅ 如果提取失败，返回文本但给出警告
                print("⚠️ 未能提取JSON数据，使用fallback")
                return {
                    "action": "search_hotels",
                    "content": content + "\n\n⚠️ 未能获取结构化数据，请尝试重新搜索",
                    "data": self._generate_smart_mock_hotels(preferences, max_hotel_price),
                    "suggestions": ["重新搜索", "更改条件"]
                }
        else:
            return self._generate_fallback_response("hotel", context, preferences)

    def _handle_flight_search(self, context: str, preferences: Dict) -> Dict:
        """处理航班搜索 - 带智能预算控制"""

        # ✅ 获取预算信息
        total_budget = preferences.get("budget", 5000) if preferences else 5000
        remaining_budget = preferences.get("remaining_budget", total_budget) if preferences else total_budget
        days = preferences.get("days", 3) if preferences else 3

        # ✅ 计算合理的航班价格范围
        budget_allocation = self._calculate_budget_allocation(total_budget, remaining_budget, days)
        max_flight_price = int(budget_allocation["flight_max"])

        # 确保价格合理（最低200，最高不超过剩余预算的50%）
        max_flight_price = max(200, min(max_flight_price, int(remaining_budget * 0.5)))

        prompt = f"""
你是专业的航班查询助手。用户需求：{context}

🎯 重要预算信息：
- 用户总预算：¥{total_budget}
- 剩余预算：¥{remaining_budget}
- 建议航班预算：¥{max_flight_price}以内

⚠️ 请注意：
1. 推荐的航班价格要合理，不能把预算全部花在机票上
2. 价格应该控制在 ¥200 - ¥{max_flight_price}
3. 优先推荐经济舱，商务舱和头等舱价格太高

请按以下格式返回：

【文字介绍】
（这里写航班推荐说明，强调性价比）

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
      "departure_date": "出发日期(YYYY-MM-DD)",
      "duration": "飞行时长",
      "price": 价格数字(控制在{max_flight_price}以内),
      "cabin_class": "经济舱",
      "stops": 0,
      "aircraft": "机型",
      "available_seats": 座位数
    }}
  ]
}}
```

要求：
1. 推荐5个航班选项
2. 价格必须在¥200-¥{max_flight_price}之间
3. 优先推荐直飞和经济舱
4. JSON格式必须严格遵守
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")

            # ✅ 提取JSON数据
            flights_data = self._extract_json_from_response(content, "flights")

            if flights_data:
                # ✅ 过滤价格过高的航班
                filtered_flights = [
                    flight for flight in flights_data
                    if 200 <= flight.get('price', 0) <= max_flight_price * 1.2
                ]

                if not filtered_flights:
                    filtered_flights = self._adjust_flight_prices(flights_data, max_flight_price)

                print(f"✅ 成功提取到 {len(filtered_flights)} 个航班数据（已过滤价格）")

                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON数据】", "").replace("【文字介绍】", "").strip()

                return {
                    "action": "search_flights",
                    "content": text_part + f"\n\n💡 **预算提示**: 建议航班预算为 ¥{max_flight_price}，为您精选了性价比高的选择。",
                    "data": filtered_flights,
                    "suggestions": [
                        "查看返程航班",
                        "了解行李政策",
                        "选择座位"
                    ]
                }
            else:
                print("⚠️ 未能提取JSON数据，使用fallback")
                return {
                    "action": "search_flights",
                    "content": content + "\n\n⚠️ 未能获取结构化数据",
                    "data": self._generate_smart_mock_flights(preferences, max_flight_price),
                    "suggestions": ["重新搜索"]
                }
        else:
            return self._generate_fallback_response("flight", context, preferences)

    # ✅ 新增：调整酒店价格到合理范围
    def _adjust_hotel_prices(self, hotels: List[Dict], max_price: int) -> List[Dict]:
        """调整酒店价格到合理范围"""
        adjusted = []
        for hotel in hotels:
            adjusted_hotel = hotel.copy()
            current_price = hotel.get('price', 500)

            if current_price > max_price:
                # 降低到最大价格的80%
                adjusted_hotel['price'] = int(max_price * 0.8)
            elif current_price < 100:
                # 提高到至少100
                adjusted_hotel['price'] = 100

            adjusted.append(adjusted_hotel)

        return adjusted

    # ✅ 新增：调整航班价格到合理范围
    def _adjust_flight_prices(self, flights: List[Dict], max_price: int) -> List[Dict]:
        """调整航班价格到合理范围"""
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

    # ✅ 改进的智能Mock数据生成
    def _generate_smart_mock_hotels(self, preferences: Dict, max_price: int) -> List[Dict]:
        """生成智能价格的模拟酒店数据"""
        print(f"⚠️ 生成智能fallback酒店数据（最高价格: ¥{max_price}）")

        destination = preferences.get("destination", "目的地") if preferences else "目的地"

        # 生成3个不同价位的酒店
        price_ranges = [
            int(max_price * 0.3),  # 低价位
            int(max_price * 0.6),  # 中价位
            int(max_price * 0.9)   # 高价位
        ]

        hotels = []
        hotel_templates = [
            {"name": f"{destination}经济型连锁酒店", "type": "经济型", "rating": 3.8},
            {"name": f"{destination}商务精选酒店", "type": "商务型", "rating": 4.2},
            {"name": f"{destination}品质生活酒店", "type": "舒适型", "rating": 4.5}
        ]

        for idx, (template, price) in enumerate(zip(hotel_templates, price_ranges)):
            hotels.append({
                "id": f"hotel_{idx+1:03d}",
                "name": template["name"],
                "location": f"{destination}市中心",
                "address": f"{destination}市XX路{100+idx*50}号",
                "tel": f"400-{1000+idx:04d}-{5000+idx:04d}",
                "price": price,
                "rating": template["rating"],
                "amenities": ["免费WiFi", "24小时前台", "空调"] if idx == 0 else
                            ["免费WiFi", "健身房", "商务中心", "停车场"] if idx == 1 else
                            ["免费WiFi", "健身房", "游泳池", "商务中心", "停车场", "早餐"],
                "landmark": f"距离地铁站{0.3+idx*0.2:.1f}公里",
                "description": f"{template['type']}，性价比高"
            })

        return hotels

    def _generate_smart_mock_flights(self, preferences: Dict, max_price: int) -> List[Dict]:
        """生成智能价格的模拟航班数据"""
        print(f"⚠️ 生成智能fallback航班数据（最高价格: ¥{max_price}）")

        origin = preferences.get("origin", "北京") if preferences else "北京"
        destination = preferences.get("destination", "上海") if preferences else "上海"

        # 生成3个不同价位的航班
        price_ranges = [
            int(max_price * 0.4),  # 低价位
            int(max_price * 0.7),  # 中价位
            int(max_price * 0.95)  # 高价位
        ]

        airlines = [
            {"code": "MU", "name": "东方航空"},
            {"code": "CA", "name": "中国国航"},
            {"code": "CZ", "name": "南方航空"}
        ]

        flights = []
        departure_times = ["08:30", "13:45", "18:20"]

        for idx, (airline, price, dep_time) in enumerate(zip(airlines, price_ranges, departure_times)):
            # 计算到达时间（假设飞行2.5小时）
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
                "duration": "2小时30分钟",
                "price": price,
                "cabin_class": "经济舱",
                "stops": 0,
                "aircraft": "波音737" if idx == 0 else "空客A320" if idx == 1 else "波音787",
                "available_seats": 20 + idx * 5
            })

        return flights

    # 继续使用原有的其他方法...
    def _handle_full_planning(self, context: str, preferences: Dict) -> Dict:
        """处理完整行程规划"""
        prompt = f"""
你是专业的旅行规划师。用户需求：{context}

请为用户制定详细的旅行计划，包括：
1. 每日行程安排（上午、下午、晚上）
2. 景点推荐和游玩建议
3. 用餐建议
4. 交通建议
5. 注意事项

请用清晰、友好的语言，使用markdown格式返回。
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            return {
                "action": "full_planning",
                "content": content,
                "data": self._extract_planning_data(content),
                "suggestions": [
                    "查看酒店推荐",
                    "查询航班信息",
                    "了解当地天气"
                ]
            }
        else:
            return {
                "action": "full_planning",
                "content": self._generate_fallback_planning(context, preferences),
                "data": None,
                "suggestions": ["重新生成", "修改需求"]
            }

    def _handle_weather_query(self, context: str, preferences: Dict) -> Dict:
        """处理天气查询"""
        prompt = f"""
你是专业的天气助手。用户需求：{context}

请提供天气信息，并按以下JSON格式返回：

【文字说明】
（这里写天气概况和建议）

【JSON数据】
```json
{{
  "city": "城市名",
  "location": "城市名",
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
                        "查看未来一周天气",
                        "了解穿衣建议",
                        "查看日出日落"
                    ]
                }
            else:
                return {
                    "action": "weather",
                    "content": content,
                    "data": self._generate_mock_weather(preferences),
                    "suggestions": ["重新查询"]
                }
        else:
            return self._generate_fallback_response("weather", context, preferences)

    def _handle_attraction_query(self, context: str, preferences: Dict) -> Dict:
        """处理景点查询"""
        prompt = f"""
你是专业的旅游顾问。用户需求：{context}

请推荐景点，并提供详细的游玩建议。包括：
1. 景点名称和特色
2. 开放时间和门票价格
3. 游玩建议和注意事项
4. 交通指引

请用markdown格式返回。
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            return {
                "action": "attraction",
                "content": content,
                "data": None,
                "suggestions": [
                    "查看附近酒店",
                    "了解当地美食",
                    "查看交通路线"
                ]
            }
        else:
            return {
                "action": "attraction",
                "content": "正在为您搜索景点信息...",
                "data": None,
                "suggestions": ["重试", "更改目的地"]
            }

    def _handle_general_query(self, context: str, preferences: Dict) -> Dict:
        """处理一般性查询"""
        prompt = f"""
你是友好的旅行助手。用户问题：{context}

请用简洁、友好的语言回答用户的问题。
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
                "content": "抱歉，AI服务暂时不可用。请稍后重试或尝试更具体的问题。",
                "data": None,
                "suggestions": ["重新提问", "查看帮助", "联系支持"]
            }

    def _extract_json_from_response(self, content: str, key: str, is_dict: bool = False) -> Any:
        """从AI响应中提取JSON数据"""
        try:
            # 方法1：提取```json```代码块
            json_match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', content, re.MULTILINE)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)

                if is_dict:
                    return data if key in str(data) else None
                else:
                    return data.get(key, [])

            # 方法2：查找第一个完整的JSON对象
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                if is_dict:
                    return data
                else:
                    return data.get(key, [])

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
        except Exception as e:
            print(f"❌ 提取JSON失败: {e}")

        return None if is_dict else []

    def _call_deepseek_api(self, prompt: str, max_retries: int = 3) -> Dict:
        """调用DeepSeek API"""
        print("🚀 调用DeepSeek API...")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一位专业、友好的旅行助手。你会根据用户的预算给出合理的建议，不会推荐价格过高的选项。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 3000
        }

        for attempt in range(max_retries):
            try:
                print(f"📡 尝试第 {attempt + 1}/{max_retries} 次请求...")

                response = requests.post(
                    f"{self.base_url}/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=60
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    print(f"✅ API响应成功，长度：{len(content)}字符")
                    return {"content": content}
                elif response.status_code == 429:
                    print(f"⚠️ API速率限制，等待后重试...")
                    wait_time = 5 * (attempt + 1)
                    time.sleep(wait_time)
                elif response.status_code == 401:
                    print(f"❌ API密钥无效")
                    return {"error": "API密钥无效"}
                else:
                    print(f"❌ API返回错误: {response.status_code} - {response.text[:200]}")
                    if attempt < max_retries - 1:
                        print("等待后重试...")
                        time.sleep(3)

            except requests.exceptions.Timeout:
                print(f"⚠️ 请求超时 (尝试 {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    print("等待后重试...")
                    time.sleep(3)

            except requests.exceptions.ConnectionError as e:
                print(f"⚠️ 连接错误: {e}")
                if attempt < max_retries - 1:
                    print("等待后重试...")
                    time.sleep(3)

            except Exception as e:
                print(f"❌ 调用DeepSeek API失败: {e}")
                break

        print("❌ 所有重试都失败了")
        return {"error": "API调用失败，请检查网络连接或稍后重试"}

    # ==================== Fallback生成函数 ====================

    def _generate_fallback_planning(self, context: str, preferences: Dict) -> str:
        """生成备用的行程规划"""
        destination = preferences.get("destination", "目的地") if preferences else "目的地"
        days = preferences.get("days", 3) if preferences else 3
        budget = preferences.get("budget", 5000) if preferences else 5000

        return f"""
🗺️ **{destination}旅行计划**

虽然AI服务暂时不可用，但我为您准备了一个参考行程框架：

📅 **行程概览**
- 目的地：{destination}
- 天数：{days}天
- 预算：¥{budget}

🌟 **Day 1 - 抵达与初探**
• 上午：抵达{destination}，酒店办理入住
• 下午：游览市中心主要景点
• 晚上：品尝当地特色美食

🌟 **Day 2 - 深度游览**  
• 上午：参观著名文化景点
• 下午：体验当地特色活动
• 晚上：逛夜市或商业街

🌟 **Day 3 - 自由探索** 
• 上午：自由活动或补充游览
• 下午：购物和准备返程
• 晚上：返程

💡 **温馨提示**
1. 建议提前预订酒店和门票
2. 准备好必要的旅行证件
3. 了解当地天气，准备合适衣物
4. 下载离线地图以备不时之需

📄 您可以点击"重新生成"获取更详细的AI定制行程。
"""

    def _generate_fallback_response(self, type: str, context: str, preferences: Dict) -> Dict:
        """生成备用响应"""
        fallback_messages = {
            "hotel": "正在为您搜索合适的酒店，请稍候...",
            "flight": "正在查询航班信息，请稍候...",
            "weather": "正在获取天气信息，请稍候...",
            "attraction": "正在搜索景点信息，请稍候...",
            "general": "我正在处理您的请求，请稍候..."
        }

        return {
            "action": type,
            "content": fallback_messages.get(type, "处理中..."),
            "data": None,
            "suggestions": ["重试", "换个问题", "查看帮助"]
        }

    def _extract_planning_data(self, content: str) -> Dict:
        """从AI生成的内容中提取结构化数据"""
        data = {
            "destination": "",
            "days": 0,
            "budget": 0,
            "itinerary": {}
        }

        if "天" in content:
            import re
            days_match = re.search(r'(\d+)天', content)
            if days_match:
                data["days"] = int(days_match.group(1))

        return data if any(data.values()) else None

    def _generate_suggestions(self, context: str) -> List[str]:
        """生成相关建议"""
        suggestions = []

        if "酒店" in context or "住" in context:
            suggestions.extend(["查看更多酒店选项", "了解酒店位置", "查看用户评价"])
        elif "航班" in context or "机票" in context:
            suggestions.extend(["查看返程航班", "了解行李政策", "选择座位"])
        elif "天气" in context:
            suggestions.extend(["查看未来一周天气", "了解穿衣建议", "查看日出日落时间"])
        else:
            suggestions.extend(["告诉我更多需求", "查看热门推荐", "开始规划行程"])

        return suggestions[:3]

    def _generate_mock_weather(self, preferences: Dict) -> Dict:
        """生成模拟天气数据"""
        print("⚠️ 使用fallback天气数据")
        destination = preferences.get("destination", "示例城市") if preferences else "示例城市"

        return {
            "city": destination,
            "location": destination,
            "temperature": 20,
            "feels_like": 18,
            "weather": "晴",
            "description": "晴",
            "humidity": 60,
            "wind_speed": "3.0 m/s",
            "forecast": [
                {"date": "明天", "temp_high": 22, "temp_low": 16, "weather": "晴", "description": "晴"},
                {"date": "后天", "temp_high": 23, "temp_low": 17, "weather": "多云", "description": "多云"}
            ]
        }


# 导出Agent类
__all__ = ['TravelAgent']