"""
TripPilot Travel Agent - 更新版
更新内容：增强机票数据生成，包含起飞地和目的地信息
"""

import json
import time
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from config.config import Config

class TravelAgent:
    """智能旅行助手Agent"""

    def __init__(self):
        """初始化Agent"""
        print("🚀 初始化TripPilot Agent...")

        # 初始化配置
        self.config = Config()
        self.api_key = Config.DEEPSEEK_API_KEY
        self.base_url = Config.DEEPSEEK_BASE_URL
        self.model = Config.DEEPSEEK_MODEL

        # 初始化工具状态
        self.init_tools()

        # 对话历史
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

    def process_message(self, message: str, preferences: Dict = None) -> Dict:
        """
        处理用户消息

        Args:
            message: 用户输入
            preferences: 用户偏好设置

        Returns:
            响应字典
        """
        print("=" * 60)
        print(f"📥 收到用户消息: {message}")

        # 添加偏好信息到消息
        if preferences:
            context = self._build_context(message, preferences)
        else:
            context = message

        # 识别意图
        intent = self._identify_intent(message)
        print(f"🎯 识别意图: {intent}")

        # 根据意图处理
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
                context_parts.append(f"预算: ¥{preferences['budget']}")
            if preferences.get("start_date") and preferences.get("end_date"):
                context_parts.append(f"日期: {preferences['start_date']} 至 {preferences['end_date']}")

        return " | ".join(context_parts)

    def _identify_intent(self, message: str) -> str:
        """识别用户意图"""
        message_lower = message.lower()

        # 关键词映射
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

    def _handle_full_planning(self, context: str, preferences: Dict) -> Dict:
        """处理完整行程规划"""
        prompt = f"""
你是一位专业的旅行规划师。请根据以下信息，为用户制定一份详细的旅行计划。

用户需求：{context}

请提供一份包含以下内容的详细行程：
1. 每日详细行程安排（包括时间、地点、活动）
2. 推荐的酒店和住宿
3. 交通安排建议
4. 美食推荐
5. 预算估算
6. 注意事项和旅行贴士

请用友好、专业的语气回复，使用清晰的格式（可以使用emoji让内容更生动）。
"""

        # 调用AI生成响应
        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            return {
                "action": "full_planning",
                "content": ai_response.get("content", ""),
                "data": self._extract_planning_data(ai_response.get("content", "")),
                "suggestions": [
                    "查看推荐的酒店",
                    "搜索相关航班",
                    "了解当地天气"
                ]
            }
        else:
            # 如果API调用失败，返回更好的提示
            return {
                "action": "full_planning",
                "content": self._generate_fallback_planning(context, preferences),
                "data": None,
                "suggestions": [
                    "重新尝试生成行程",
                    "手动搜索酒店",
                    "查看热门景点"
                ]
            }

    def _handle_hotel_search(self, context: str, preferences: Dict) -> Dict:
        """处理酒店搜索"""
        prompt = f"""
请为用户推荐符合以下条件的酒店：

{context}

请推荐5个不同档次的酒店，包含：
- 酒店名称
- 地理位置
- 价格范围
- 特色和优势
- 用户评分

用友好的语气介绍，并说明推荐理由。
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            return {
                "action": "search_hotels",
                "content": ai_response.get("content", ""),
                "data": self._generate_mock_hotels(preferences),
                "suggestions": [
                    "查看更多酒店",
                    "调整价格范围",
                    "查看用户评价"
                ]
            }
        else:
            return self._generate_fallback_response("hotel", context, preferences)

    def _handle_flight_search(self, context: str, preferences: Dict) -> Dict:
        """处理航班搜索"""
        prompt = f"""
请为用户查询符合以下条件的航班：

{context}

请提供航班信息，包含：
- 航班号
- 起飞和到达时间
- 航空公司
- 价格范围
- 飞行时长

用友好的语气介绍。
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            return {
                "action": "search_flights",
                "content": ai_response.get("content", ""),
                "data": self._generate_mock_flights(preferences),
                "suggestions": [
                    "查看返程航班",
                    "调整出发时间",
                    "比较不同航空公司"
                ]
            }
        else:
            fallback = self._generate_fallback_response("flight", context, preferences)
            fallback["data"] = self._generate_mock_flights(preferences)
            return fallback

    def _handle_weather_query(self, context: str, preferences: Dict) -> Dict:
        """处理天气查询"""
        prompt = f"""
请为用户提供天气信息：

{context}

请包含：
- 当前天气状况
- 未来几天天气预报
- 穿衣建议
- 旅行注意事项

用友好的语气回复。
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            return {
                "action": "weather",
                "content": ai_response.get("content", ""),
                "data": self._generate_mock_weather(preferences),
                "suggestions": [
                    "查看更多天气详情",
                    "了解最佳旅行季节",
                    "开始规划行程"
                ]
            }
        else:
            fallback = self._generate_fallback_response("weather", context, preferences)
            fallback["data"] = self._generate_mock_weather(preferences)
            return fallback

    def _handle_attraction_query(self, context: str, preferences: Dict) -> Dict:
        """处理景点查询"""
        prompt = f"""
请为用户推荐景点：

{context}

请包含：
- 必游景点推荐
- 景点特色介绍
- 游玩建议和最佳时间
- 门票价格参考

用友好的语气回复。
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            return {
                "action": "attraction",
                "content": ai_response.get("content", ""),
                "data": None,
                "suggestions": [
                    "查看更多景点",
                    "规划游览路线",
                    "搜索附近酒店"
                ]
            }
        else:
            return self._generate_fallback_response("attraction", context, preferences)

    def _handle_general_query(self, context: str, preferences: Dict) -> Dict:
        """处理一般查询"""
        prompt = f"""
作为专业的旅行助手，请回答用户的问题：

{context}

请提供详细、有用的信息，如果涉及具体的旅行建议，请给出实用的推荐。
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            return {
                "action": "general",
                "content": ai_response.get("content", ""),
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
                {"role": "system", "content": "你是一位专业、友好的旅行助手。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
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

    def _generate_fallback_planning(self, context: str, preferences: Dict) -> str:
        """生成备用的行程规划（当API失败时）"""
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

🔄 您可以点击"重新生成"获取更详细的AI定制行程。
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

        # 简单的提取逻辑示例
        if "天" in content:
            import re
            days_match = re.search(r'(\d+)天', content)
            if days_match:
                data["days"] = int(days_match.group(1))

        return data if any(data.values()) else None

    def _generate_mock_hotels(self, preferences: Dict) -> List[Dict]:
        """生成模拟酒店数据"""
        destination = preferences.get("destination", "城市") if preferences else "城市"
        budget = preferences.get("budget", 5000) if preferences else 5000

        hotels = [
            {
                "id": "hotel_001",
                "name": f"{destination}希尔顿酒店",
                "location": f"{destination}市中心",
                "address": f"{destination}市中心商业区88号",
                "tel": "400-820-0000",
                "price": int(budget * 0.15),
                "rating": 4.8,
                "amenities": ["免费WiFi", "健身房", "游泳池", "商务中心", "早餐"]
            },
            {
                "id": "hotel_002",
                "name": f"{destination}商务酒店",
                "location": f"{destination}商业区",
                "address": f"{destination}商业区中心路123号",
                "tel": "400-123-4567",
                "price": int(budget * 0.1),
                "rating": 4.2,
                "amenities": ["免费WiFi", "早餐", "停车场"]
            },
            {
                "id": "hotel_003",
                "name": f"{destination}精品民宿",
                "location": f"{destination}老城区",
                "address": f"{destination}老城区文化街45号",
                "tel": "400-888-9999",
                "price": int(budget * 0.08),
                "rating": 4.5,
                "amenities": ["特色装修", "本地体验", "免费WiFi"]
            },
            {
                "id": "hotel_004",
                "name": f"{destination}快捷酒店",
                "location": f"{destination}火车站附近",
                "address": f"{destination}火车站广场1号",
                "tel": "400-666-7777",
                "price": int(budget * 0.05),
                "rating": 4.0,
                "amenities": ["免费WiFi", "24小时前台"]
            },
            {
                "id": "hotel_005",
                "name": f"{destination}豪华度假酒店",
                "location": f"{destination}景区旁",
                "address": f"{destination}风景区入口处",
                "tel": "400-999-0000",
                "price": int(budget * 0.2),
                "rating": 4.9,
                "amenities": ["免费WiFi", "健身房", "游泳池", "SPA", "景区接送", "豪华早餐"]
            }
        ]

        return hotels

    def _generate_mock_flights(self, preferences: Dict) -> List[Dict]:
        """
        生成模拟航班数据 - 增强版

        Args:
            preferences: 用户偏好设置

        Returns:
            航班列表
        """
        destination = preferences.get("destination", "目的地") if preferences else "目的地"
        origin = preferences.get("origin", "出发地") if preferences else "出发地"
        start_date = preferences.get("start_date", datetime.now().strftime("%Y-%m-%d"))

        # 如果没有指定出发地，根据目的地智能推断
        if origin == "出发地":
            # 常见的出发地选择
            major_cities = ["北京", "上海", "广州", "深圳", "成都", "杭州"]
            # 如果目的地在列表中，选择另一个城市作为出发地
            if destination in major_cities:
                origin = random.choice([c for c in major_cities if c != destination])
            else:
                origin = "北京"  # 默认北京出发

        # 航空公司列表
        airlines = [
            {"code": "CA", "name": "中国国航"},
            {"code": "MU", "name": "东方航空"},
            {"code": "CZ", "name": "南方航空"},
            {"code": "HU", "name": "海南航空"},
            {"code": "3U", "name": "四川航空"},
        ]

        flights = []
        base_times = ["07:30", "09:45", "12:00", "14:30", "17:15", "19:40"]

        for i, (time_str, airline) in enumerate(zip(base_times[:5], airlines)):
            # 计算到达时间（假设飞行2-3小时）
            hour, minute = map(int, time_str.split(":"))
            flight_duration = random.randint(120, 180)  # 2-3小时
            arrival_hour = hour + flight_duration // 60
            arrival_minute = minute + flight_duration % 60
            if arrival_minute >= 60:
                arrival_hour += 1
                arrival_minute -= 60
            arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"

            # 价格随时间段变化
            base_price = random.randint(800, 2500)

            flights.append({
                "id": f"flight_{i+1:03d}",
                "carrier_code": airline["code"],
                "carrier_name": airline["name"],
                "flight_number": f"{random.randint(10000, 99999)}",  # ✅ 修改为5位数航班号
                "origin": origin,  # ✅ 添加起飞地
                "destination": destination,  # ✅ 添加目的地
                "departure_time": time_str,
                "arrival_time": arrival_time,
                "departure_date": start_date,
                "duration": f"{flight_duration // 60}小时{flight_duration % 60}分钟",
                "price": base_price,
                "total_price": base_price,
                "cabin_class": "经济舱",
                "stops": 0,
                "aircraft": random.choice(["波音737", "空客A320", "波音787", "空客A330"]),
                "available_seats": random.randint(5, 30)
            })

        # 按价格排序
        flights.sort(key=lambda x: x["price"])

        return flights

    def _generate_mock_weather(self, preferences: Dict) -> Dict:
        """生成模拟天气数据"""
        destination = preferences.get("destination", "目的地") if preferences else "目的地"

        # 根据月份生成合理的温度范围
        month = datetime.now().month

        # 温度基准
        if month in [12, 1, 2]:  # 冬季
            base_temp = random.randint(0, 10)
            weather_options = ["晴", "多云", "阴", "小雪", "晴转多云"]
        elif month in [3, 4, 5]:  # 春季
            base_temp = random.randint(15, 25)
            weather_options = ["晴", "多云", "小雨", "晴转多云", "阴"]
        elif month in [6, 7, 8]:  # 夏季
            base_temp = random.randint(28, 35)
            weather_options = ["晴", "多云", "雷阵雨", "晴转多云", "大雨"]
        else:  # 秋季
            base_temp = random.randint(15, 25)
            weather_options = ["晴", "多云", "小雨", "晴转多云", "阴"]

        # 根据城市名调整
        temp_adjustment = 0
        if any(city in destination for city in ["三亚", "海南", "广州", "深圳"]):
            temp_adjustment = 8
        elif any(city in destination for city in ["哈尔滨", "长春", "沈阳"]):
            temp_adjustment = -10
        elif any(city in destination for city in ["昆明", "丽江"]):
            temp_adjustment = -3

        temperature = base_temp + temp_adjustment
        feels_like = temperature + random.randint(-3, 3)

        weather_data = {
            "city": destination,
            "location": destination,
            "temperature": temperature,
            "feels_like": feels_like,
            "weather": random.choice(weather_options),
            "description": random.choice(weather_options),
            "humidity": random.randint(40, 85),
            "wind_speed": f"{random.uniform(1.0, 8.0):.1f} m/s",
            "wind_direction": random.choice(["东风", "西风", "南风", "北风", "东南风", "西北风"]),
            "visibility": f"{random.randint(8, 20)} km",
            "pressure": f"{random.randint(1000, 1025)} hPa",
            "uv_index": random.randint(1, 11),
            "sunrise": "06:30",
            "sunset": "18:45",
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "forecast": self._generate_forecast(temperature, weather_options)
        }

        return weather_data

    def _generate_forecast(self, base_temp: int, weather_options: list) -> List[Dict]:
        """生成未来几天的天气预报"""
        forecast = []

        for i in range(1, 5):
            date = datetime.now() + timedelta(days=i)
            weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]

            temp_high = base_temp + random.randint(0, 5)
            temp_low = base_temp - random.randint(3, 8)

            forecast.append({
                "date": f"{date.month}/{date.day} {weekday}",
                "temp_high": temp_high,
                "temp_low": temp_low,
                "weather": random.choice(weather_options),
                "description": random.choice(weather_options)
            })

        return forecast

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

# 导出Agent类
__all__ = ['TravelAgent']