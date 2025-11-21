"""
TripPilot Travel Agent - 修复版
核心改进：让DeepSeek直接返回结构化JSON数据
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
                context_parts.append(f"预算: ¥{preferences['budget']}")
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
        """处理酒店搜索 - 关键修复：要求DeepSeek返回JSON"""

        # ✅ 修改prompt，明确要求返回JSON格式
        prompt = f"""
你是专业的酒店推荐助手。用户需求：{context}

请按以下格式返回，先用自然语言介绍，然后提供JSON数据：

【文字介绍】
（这里写推荐理由和说明）

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
      "price": 价格数字,
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
2. 价格要符合用户预算
3. JSON格式必须严格遵守，不要有语法错误
4. 每个字段都要填写完整
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")

            # ✅ 提取JSON数据
            hotels_data = self._extract_json_from_response(content, "hotels")

            if hotels_data:
                print(f"✅ 成功提取到 {len(hotels_data)} 个酒店数据")

                # ✅ 提取文字部分（JSON之前的内容）
                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON数据】", "").replace("【文字介绍】", "").strip()

                return {
                    "action": "search_hotels",
                    "content": text_part,
                    "data": hotels_data,
                    "suggestions": [
                        "查看更多酒店",
                        "调整价格范围",
                        "查看用户评价"
                    ]
                }
            else:
                # ✅ 如果提取失败，返回文本但给出警告
                print("⚠️ 未能提取JSON数据，仅返回文本")
                return {
                    "action": "search_hotels",
                    "content": content + "\n\n⚠️ 未能获取结构化数据，请尝试重新搜索",
                    "data": self._generate_mock_hotels(preferences),  # fallback
                    "suggestions": ["重新搜索", "更改条件"]
                }
        else:
            return self._generate_fallback_response("hotel", context, preferences)

    def _handle_flight_search(self, context: str, preferences: Dict) -> Dict:
        """处理航班搜索 - 同样要求返回JSON"""

        prompt = f"""
你是专业的航班查询助手。用户需求：{context}

请按以下格式返回：

【文字介绍】
（这里写航班推荐说明）

【JSON数据】
```json
{{
  "flights": [
    {{
      "id": "flight_001",
      "carrier_code": "CA",
      "carrier_name": "中国国航",
      "flight_number": "1234",
      "origin": "出发地",
      "destination": "目的地",
      "departure_time": "08:30",
      "arrival_time": "11:00",
      "departure_date": "2025-01-15",
      "duration": "2小时30分钟",
      "price": 850,
      "cabin_class": "经济舱",
      "stops": 0,
      "aircraft": "波音737",
      "available_seats": 25
    }}
  ]
}}
```

要求：
1. 推荐5个真实的航班
2. 时间和价格要合理
3. JSON格式严格正确
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            flights_data = self._extract_json_from_response(content, "flights")

            if flights_data:
                print(f"✅ 成功提取到 {len(flights_data)} 个航班数据")
                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON数据】", "").replace("【文字介绍】", "").strip()

                return {
                    "action": "search_flights",
                    "content": text_part,
                    "data": flights_data,
                    "suggestions": [
                        "查看返程航班",
                        "调整出发时间",
                        "比较不同航空公司"
                    ]
                }
            else:
                print("⚠️ 未能提取JSON数据")
                fallback = self._generate_fallback_response("flight", context, preferences)
                fallback["data"] = self._generate_mock_flights(preferences)
                return fallback
        else:
            fallback = self._generate_fallback_response("flight", context, preferences)
            fallback["data"] = self._generate_mock_flights(preferences)
            return fallback

    def _handle_weather_query(self, context: str, preferences: Dict) -> Dict:
        """处理天气查询 - 返回JSON格式"""

        prompt = f"""
你是天气信息助手。用户需求：{context}

请按以下格式返回：

【文字介绍】
（这里写天气概况和建议）

【JSON数据】
```json
{{
  "weather": {{
    "city": "城市名",
    "location": "城市名",
    "temperature": 22,
    "feels_like": 20,
    "weather": "晴朗",
    "description": "晴朗",
    "humidity": 65,
    "wind_speed": "3.5 m/s",
    "wind_direction": "东风",
    "visibility": "15 km",
    "pressure": "1013 hPa",
    "uv_index": 5,
    "sunrise": "06:30",
    "sunset": "18:45",
    "update_time": "2025-11-21 14:30",
    "forecast": [
      {{
        "date": "11/22 周五",
        "temp_high": 25,
        "temp_low": 18,
        "weather": "多云",
        "description": "多云"
      }},
      {{
        "date": "11/23 周六",
        "temp_high": 23,
        "temp_low": 17,
        "weather": "晴",
        "description": "晴"
      }},
      {{
        "date": "11/24 周日",
        "temp_high": 24,
        "temp_low": 16,
        "weather": "晴",
        "description": "晴"
      }},
      {{
        "date": "11/25 周一",
        "temp_high": 26,
        "temp_low": 19,
        "weather": "多云",
        "description": "多云"
      }}
    ]
  }}
}}
```

要求：必须包含4天的预报数据
"""

        ai_response = self._call_deepseek_api(prompt)

        if ai_response and "error" not in ai_response:
            content = ai_response.get("content", "")
            weather_data = self._extract_json_from_response(content, "weather")

            if weather_data:
                print(f"✅ 成功提取天气数据")
                text_part = content.split("```json")[0].strip()
                text_part = text_part.replace("【JSON数据】", "").replace("【文字介绍】", "").strip()

                return {
                    "action": "weather",
                    "content": text_part,
                    "data": weather_data,
                    "suggestions": [
                        "查看更多天气详情",
                        "了解最佳旅行季节",
                        "开始规划行程"
                    ]
                }
            else:
                print("⚠️ 未能提取天气JSON数据")
                fallback = self._generate_fallback_response("weather", context, preferences)
                fallback["data"] = self._generate_mock_weather(preferences)
                return fallback
        else:
            fallback = self._generate_fallback_response("weather", context, preferences)
            fallback["data"] = self._generate_mock_weather(preferences)
            return fallback

    def _extract_json_from_response(self, content: str, key: str) -> Any:
        """
        从DeepSeek响应中提取JSON数据

        Args:
            content: DeepSeek返回的完整文本
            key: 要提取的顶层键名 (hotels/flights/weather等)

        Returns:
            提取的数据，如果失败返回None
        """
        try:
            # 方法1: 查找 ```json 代码块
            json_match = re.search(r'```json\s*(\{.*?\})\s*```', content, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)

                # 返回指定key的数据
                if key in data:
                    return data[key]
                else:
                    print(f"⚠️ JSON中没有找到key: {key}")
                    return None

            # 方法2: 尝试直接解析整个内容
            try:
                data = json.loads(content)
                if key in data:
                    return data[key]
            except:
                pass

            print("⚠️ 无法从响应中提取JSON")
            return None

        except json.JSONDecodeError as e:
            print(f"❌ JSON解析失败: {e}")
            return None
        except Exception as e:
            print(f"❌ 提取JSON时出错: {e}")
            return None

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

    # ==================== Fallback生成函数（仅在API失败时使用） ====================

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

    # ==================== Mock数据生成（仅作为fallback） ====================

    def _generate_mock_hotels(self, preferences: Dict) -> List[Dict]:
        """生成模拟酒店数据（仅在DeepSeek失败时使用）"""
        print("⚠️ 使用fallback mock数据")
        return [
            {
                "id": "hotel_001",
                "name": "示例酒店1",
                "location": "市中心",
                "address": "示例地址1号",
                "tel": "400-000-0001",
                "price": 500,
                "rating": 4.5,
                "amenities": ["免费WiFi", "早餐"],
                "landmark": "近地铁站",
                "description": "示例数据"
            }
        ]

    def _generate_mock_flights(self, preferences: Dict) -> List[Dict]:
        """生成模拟航班数据（仅在DeepSeek失败时使用）"""
        print("⚠️ 使用fallback mock数据")
        return [
            {
                "id": "flight_001",
                "carrier_code": "XX",
                "carrier_name": "示例航空",
                "flight_number": "0000",
                "origin": "出发地",
                "destination": "目的地",
                "departure_time": "08:00",
                "arrival_time": "10:00",
                "departure_date": str(datetime.now().date()),
                "duration": "2小时",
                "price": 800,
                "cabin_class": "经济舱",
                "stops": 0,
                "aircraft": "波音737",
                "available_seats": 20
            }
        ]

    def _generate_mock_weather(self, preferences: Dict) -> Dict:
        """生成模拟天气数据（仅在DeepSeek失败时使用）"""
        print("⚠️ 使用fallback mock数据")
        return {
            "city": "示例城市",
            "location": "示例城市",
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