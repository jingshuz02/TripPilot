"""
改进版 TripPilot Agent - 真正的智能旅行规划系统
解决核心问题：
1. 智能意图理解与多步骤规划
2. 用户需求精准匹配
3. 完整的行程规划能力
"""

from typing import Dict, Any, List, Optional
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum


# ==================== 数据结构定义 ====================

@dataclass
class UserPreferences:
    """用户偏好数据结构"""
    budget: float
    start_date: str
    end_date: str
    travelers: int = 1
    hotel_requirements: List[str] = None  # ["停车场", "游泳池", "健身房"]
    flight_class: str = "ECONOMY"
    interests: List[str] = None  # ["文化", "美食", "购物"]

    def __post_init__(self):
        if self.hotel_requirements is None:
            self.hotel_requirements = []
        if self.interests is None:
            self.interests = []


class IntentType(Enum):
    """意图类型枚举"""
    FLIGHT = "flight"
    HOTEL = "hotel"
    WEATHER = "weather"
    ATTRACTION = "attraction"
    RESTAURANT = "restaurant"
    ROUTE = "route"
    FULL_PLANNING = "full_planning"  # 完整行程规划
    TICKET = "ticket"  # 门票查询
    GENERAL = "general"


@dataclass
class TravelPlan:
    """完整旅行计划"""
    destination: str
    start_date: str
    end_date: str
    total_budget: float
    daily_plans: List[Dict]  # 每日行程
    hotels: List[Dict]  # 酒店列表
    flights: List[Dict]  # 航班列表
    estimated_cost: float
    recommendations: List[str]  # 建议事项


# ==================== 改进版 Agent 核心 ====================

class TravelAgent:
    """
    改进版旅行Agent
    核心改进：
    1. 多步骤规划能力
    2. 上下文记忆
    3. 需求精准匹配
    4. 统一响应格式
    """

    def __init__(self):
        """初始化Agent"""
        # 上下文管理
        self.conversation_context = []
        self.user_preferences = None
        self.current_plan = None

        # 工具初始化
        from backend.tools.travel_tools import TravelTools
        self.tools = TravelTools()

        print("✅ 改进版Agent初始化完成")

    def process(self, user_message: str, preferences: Dict = None) -> Dict[str, Any]:
        """
        主处理方法 - 改进版

        Returns:
            统一格式响应：
            {
                "action": str,  # 动作类型
                "content": str,  # 文本描述
                "data": Any,    # 结构化数据
                "suggestions": List[str],  # 后续建议
                "requires_confirmation": bool  # 是否需要确认
            }
        """
        # 1. 更新用户偏好
        if preferences:
            self.user_preferences = UserPreferences(**preferences)

        # 2. 理解意图（改进版）
        intent_result = self.understand_intent_advanced(user_message)
        intent = intent_result['intent']
        entities = intent_result['entities']

        print(f"📊 意图分析: {intent.value}")
        print(f"📦 实体提取: {entities}")

        # 3. 执行相应功能
        try:
            # 路线规划 - 修正
            if intent == IntentType.ROUTE:
                return self.handle_route_planning_fixed(entities)

            # 完整行程规划 - 新增
            elif intent == IntentType.FULL_PLANNING:
                return self.handle_full_trip_planning(entities)

            # 酒店搜索 - 增强版
            elif intent == IntentType.HOTEL:
                return self.handle_hotel_enhanced(entities)

            # 门票查询 - 新增
            elif intent == IntentType.TICKET:
                return self.handle_ticket_search(entities)

            # 航班搜索 - 修正
            elif intent == IntentType.FLIGHT:
                return self.handle_flight_enhanced(entities)

            # 其他原有功能...
            else:
                return self.handle_original_intents(intent, entities)

        except Exception as e:
            print(f"❌ 处理错误: {e}")
            return self.generate_error_response(str(e))

    def understand_intent_advanced(self, message: str) -> Dict:
        """
        改进版意图理解
        使用更智能的NLP分析
        """
        msg_lower = message.lower()
        entities = {}

        # 1. 路线规划识别（修正）
        route_keywords = ['怎么去', '路线', '导航', '从.*到', '最快.*到', '机场.*市区']
        if any(keyword in msg_lower for keyword in route_keywords):
            # 提取起点和终点
            import re
            # 匹配 "从X到Y" 模式
            pattern = r'从(.+?)到(.+?)(?:[的，。？]|$)'
            match = re.search(pattern, message)
            if match:
                entities['origin'] = match.group(1)
                entities['destination'] = match.group(2)
            # 匹配 "机场到市区" 模式
            elif '机场' in message and '市区' in message:
                entities['origin'] = '机场'
                entities['destination'] = '市区'

            return {'intent': IntentType.ROUTE, 'entities': entities}

        # 2. 完整行程规划识别
        planning_keywords = ['规划.*行程', '安排.*旅游', '制定.*计划', '整个行程', '完整.*攻略']
        if any(keyword in msg_lower for keyword in planning_keywords):
            entities = self._extract_planning_entities(message)
            return {'intent': IntentType.FULL_PLANNING, 'entities': entities}

        # 3. 酒店搜索（增强版）
        hotel_keywords = ['酒店', '住宿', '旅馆', '民宿']
        if any(word in msg_lower for word in hotel_keywords):
            entities = self._extract_hotel_requirements(message)
            return {'intent': IntentType.HOTEL, 'entities': entities}

        # 4. 门票查询
        ticket_keywords = ['门票', '票价', '开放时间', '营业时间']
        if any(word in msg_lower for word in ticket_keywords):
            entities['attraction'] = self._extract_attraction_name(message)
            return {'intent': IntentType.TICKET, 'entities': entities}

        # 5. 航班搜索
        if any(word in msg_lower for word in ['航班', '飞机', '机票', '飞往']):
            entities = self._extract_flight_info(message)
            return {'intent': IntentType.FLIGHT, 'entities': entities}

        # 其他意图...
        return {'intent': IntentType.GENERAL, 'entities': entities}

    def _extract_hotel_requirements(self, message: str) -> Dict:
        """提取酒店需求"""
        entities = {
            'city': self._extract_city(message),
            'requirements': [],
            'price_range': None
        }

        # 设施需求提取
        facilities = {
            '停车场': ['停车', '车位', 'parking'],
            '游泳池': ['游泳池', '泳池', 'pool'],
            '健身房': ['健身', 'gym'],
            '早餐': ['早餐', '早饭', 'breakfast'],
            'WiFi': ['wifi', '网络', '无线网'],
            '商务': ['商务', '会议'],
        }

        for facility, keywords in facilities.items():
            if any(kw in message.lower() for kw in keywords):
                entities['requirements'].append(facility)

        # 价格范围提取
        import re
        price_pattern = r'(\d+)[-到至](\d+)[元块]'
        match = re.search(price_pattern, message)
        if match:
            entities['price_range'] = (int(match.group(1)), int(match.group(2)))

        # 房型提取
        if '双人' in message or '标间' in message:
            entities['room_type'] = '双人间'
        elif '大床' in message:
            entities['room_type'] = '大床房'
        elif '套房' in message:
            entities['room_type'] = '套房'

        return entities

    # ==================== 核心功能处理 ====================

    def handle_route_planning_fixed(self, entities: Dict) -> Dict:
        """修正：路线规划处理"""
        origin = entities.get('origin', '当前位置')
        destination = entities.get('destination', '目的地')

        # 调用地图API获取路线
        route_info = self._get_route_info(origin, destination)

        content = f"""
### 🗺️ 路线规划：{origin} → {destination}

**推荐方案：**
"""

        # 生成多种交通方案
        options = [
            {
                'method': '地铁',
                'duration': '35分钟',
                'cost': '¥8',
                'details': '地铁5号线 → 换乘2号线',
                'pros': '快速、准时、不堵车'
            },
            {
                'method': '出租车',
                'duration': '25-40分钟',
                'cost': '¥60-80',
                'details': '直达，视路况而定',
                'pros': '舒适、直达、行李方便'
            },
            {
                'method': '机场快线',
                'duration': '30分钟',
                'cost': '¥25',
                'details': '机场快线直达市中心',
                'pros': '专线、舒适、有座位'
            }
        ]

        for i, opt in enumerate(options, 1):
            content += f"""
**{i}. {opt['method']}**
- ⏱️ 时间：{opt['duration']}
- 💰 费用：{opt['cost']}
- 📍 路线：{opt['details']}
- ✅ 优势：{opt['pros']}
"""

        return {
            'action': 'route_planning',
            'content': content,
            'data': {
                'origin': origin,
                'destination': destination,
                'routes': options,
                'recommended': options[0]
            },
            'suggestions': [
                f"建议提前预订{destination}附近的酒店",
                "记得查看实时路况",
                "高峰期建议选择地铁"
            ],
            'requires_confirmation': False
        }

    def handle_full_trip_planning(self, entities: Dict) -> Dict:
        """完整行程规划"""
        destination = entities.get('destination', '目的地')
        days = entities.get('days', 3)
        budget = entities.get('budget', 3000)

        # 生成完整行程计划
        plan = self._generate_full_itinerary(destination, days, budget)

        content = f"""
### 🎯 {destination} {days}天完整行程规划

**预算：¥{budget}** | **日期：{entities.get('start_date', '待定')}**

---
"""

        # 每日行程
        daily_plans = []
        for day in range(1, days + 1):
            day_plan = {
                'day': day,
                'morning': f'景点参观（如故宫、长城等）',
                'afternoon': f'文化体验（如胡同游、博物馆）',
                'evening': f'美食探索（如烤鸭、小吃街）',
                'accommodation': f'推荐住宿区域：王府井/三里屯',
                'transport': '地铁+步行',
                'estimated_cost': budget / days
            }
            daily_plans.append(day_plan)

            content += f"""
**第{day}天行程：**
🌅 上午：{day_plan['morning']}
☀️ 下午：{day_plan['afternoon']}
🌃 晚上：{day_plan['evening']}
🏨 住宿：{day_plan['accommodation']}
🚇 交通：{day_plan['transport']}
💰 预计花费：¥{day_plan['estimated_cost']:.0f}

"""

        # 推荐清单
        content += """
---
### 📋 必备清单

**🏨 住宿推荐（2-3晚）：**
- 经济型：如家/汉庭 (¥200-300/晚)
- 舒适型：亚朵/全季 (¥400-600/晚)
- 豪华型：万豪/希尔顿 (¥800+/晚)

**✈️ 交通安排：**
- 机票：提前预订可节省30-50%
- 市内：地铁日票¥20/天

**🎫 门票预算：**
- 主要景点：¥500-800
- 美食体验：¥600-1000

**💡 省钱技巧：**
1. 提前在线预订门票有优惠
2. 避开周末和节假日
3. 选择地铁出行最经济
"""

        # 返回完整响应
        return {
            'action': 'full_planning',
            'content': content,
            'data': {
                'destination': destination,
                'duration': days,
                'budget': budget,
                'daily_plans': daily_plans,
                'total_cost_estimate': budget * 0.9,
                'hotels': self._recommend_hotels_for_plan(destination, budget/days/3),
                'flights': self._recommend_flights_for_plan(destination),
                'attractions': self._get_top_attractions(destination)
            },
            'suggestions': [
                "建议提前2周预订机票和酒店",
                "可以根据实际情况调整每日行程",
                "记得购买旅游保险"
            ],
            'requires_confirmation': True
        }

    def handle_hotel_enhanced(self, entities: Dict) -> Dict:
        """增强版酒店搜索 - 支持筛选"""
        city = entities.get('city', '北京')
        requirements = entities.get('requirements', [])
        price_range = entities.get('price_range')

        # 获取酒店列表
        hotels = self.tools.search_hotels(city, '', '')

        # 智能筛选
        filtered_hotels = []
        for hotel in hotels:
            # 根据需求筛选
            if requirements:
                # 模拟设施匹配
                hotel['matched_requirements'] = []
                for req in requirements:
                    if req in ['停车场', 'WiFi', '早餐']:  # 假设这些酒店都有
                        hotel['matched_requirements'].append(req)

                # 计算匹配度
                hotel['match_score'] = len(hotel['matched_requirements']) / len(requirements)

                # 只保留匹配度>50%的
                if hotel['match_score'] >= 0.5:
                    filtered_hotels.append(hotel)
            else:
                filtered_hotels.append(hotel)

            # 价格筛选
            if price_range and filtered_hotels:
                filtered_hotels = [
                    h for h in filtered_hotels
                    if price_range[0] <= h.get('price', 0) <= price_range[1]
                ]

        # 生成响应
        content = f"""
### 🏨 {city}酒店搜索结果

**筛选条件：**
- 设施要求：{', '.join(requirements) if requirements else '无特殊要求'}
- 价格范围：{f'¥{price_range[0]}-{price_range[1]}' if price_range else '不限'}

找到 {len(filtered_hotels)} 家符合条件的酒店：
"""

        # 为每个酒店添加详情查看功能标记
        for i, hotel in enumerate(filtered_hotels[:5], 1):
            hotel['has_details'] = True  # 标记支持查看详情
            hotel['details_available'] = True

            match_info = ""
            if 'match_score' in hotel:
                match_info = f" | 匹配度：{hotel['match_score']:.0%}"

            content += f"""
**{i}. {hotel['name']}**
- 💰 价格：¥{hotel['price']}/晚
- 📍 位置：{hotel.get('location', hotel.get('address', ''))}
- ⭐ 评分：{hotel.get('rating', 'N/A')}
- ✅ 满足需求：{', '.join(hotel.get('matched_requirements', []))} {match_info}
- 🔍 支持查看详情
"""

        return {
            'action': 'search_hotels',
            'content': content,
            'data': filtered_hotels,
            'suggestions': [
                "点击酒店可查看详细信息",
                "可以调整筛选条件获得更多选择",
                "建议提前预订以获得优惠"
            ],
            'requires_confirmation': False
        }

    def handle_ticket_search(self, entities: Dict) -> Dict:
        """门票查询处理"""
        attraction = entities.get('attraction', '景点')

        # 模拟获取门票信息
        ticket_info = self._get_ticket_info(attraction)

        content = f"""
### 🎫 {attraction}门票信息

**基础信息：**
- 📍 地址：{ticket_info['address']}
- ⏰ 开放时间：{ticket_info['opening_hours']}
- 📞 咨询电话：{ticket_info['phone']}

**票价信息：**
"""

        for ticket_type, price in ticket_info['prices'].items():
            content += f"- {ticket_type}：¥{price}\n"

        content += f"""
**优惠政策：**
{ticket_info['discounts']}

**预订建议：**
{ticket_info['booking_tips']}

**游玩建议：**
- 建议游玩时长：{ticket_info['suggested_duration']}
- 最佳游玩时间：{ticket_info['best_time']}
"""

        return {
            'action': 'ticket_info',
            'content': content,
            'data': ticket_info,
            'suggestions': [
                "建议提前在线购票享受优惠",
                "避开周末和节假日人流高峰",
                "可以购买联票更划算"
            ],
            'requires_confirmation': False
        }

    # ==================== 辅助方法 ====================

    def _get_ticket_info(self, attraction: str) -> Dict:
        """获取门票信息（模拟数据）"""
        # 这里应该调用真实的API
        mock_data = {
            '迪士尼': {
                'address': '上海市浦东新区川沙镇',
                'opening_hours': '9:00-21:00',
                'phone': '400-180-0000',
                'prices': {
                    '成人票（平日）': 435,
                    '成人票（高峰日）': 599,
                    '儿童/老人票（平日）': 325,
                    '儿童/老人票（高峰日）': 449
                },
                'discounts': '1.0米以下儿童免费；65岁以上老人8折',
                'booking_tips': '建议提前3天在官网预订，可享95折优惠',
                'suggested_duration': '1-2天',
                'best_time': '春秋季节，避开暑假和节假日'
            },
            '海洋公园': {
                'address': '香港岛南部',
                'opening_hours': '10:00-18:00',
                'phone': '+852-3923-2323',
                'prices': {
                    '成人票': 498,
                    '儿童票(3-11岁)': 249,
                    '长者票(65岁+)': 100
                },
                'discounts': '香港居民享7折；生日当天免费入园',
                'booking_tips': 'Klook平台预订可享85折',
                'suggested_duration': '5-6小时',
                'best_time': '10-11月或3-5月，天气舒适'
            }
        }

        # 默认数据
        default = {
            'address': '景点地址',
            'opening_hours': '9:00-18:00',
            'phone': '000-0000-0000',
            'prices': {
                '成人票': 100,
                '儿童票': 50,
                '学生票': 80
            },
            'discounts': '儿童、老人、学生享受优惠',
            'booking_tips': '建议提前预订',
            'suggested_duration': '3-4小时',
            'best_time': '春秋季节'
        }

        return mock_data.get(attraction, default)

    def _extract_city(self, message: str) -> str:
        """提取城市名称"""
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '西安', '南京']
        for city in cities:
            if city in message:
                return city
        return '北京'  # 默认

    def _get_route_info(self, origin: str, destination: str) -> Dict:
        """获取路线信息"""
        # 这里应该调用真实的地图API
        return {
            'distance': '25km',
            'duration': '35分钟',
            'traffic_status': '畅通'
        }

    def _generate_full_itinerary(self, destination: str, days: int, budget: float) -> TravelPlan:
        """生成完整行程"""
        # 这里应该使用AI生成详细行程
        return TravelPlan(
            destination=destination,
            start_date='待定',
            end_date='待定',
            total_budget=budget,
            daily_plans=[],
            hotels=[],
            flights=[],
            estimated_cost=budget * 0.9,
            recommendations=[]
        )

    def _recommend_hotels_for_plan(self, destination: str, daily_budget: float) -> List[Dict]:
        """为行程推荐酒店"""
        return self.tools.search_hotels(destination, '', '')[:3]

    def _recommend_flights_for_plan(self, destination: str) -> List[Dict]:
        """为行程推荐航班"""
        return []  # 简化处理

    def _get_top_attractions(self, destination: str) -> List[Dict]:
        """获取热门景点"""
        return self.tools.search_attractions(destination)[:5]

    def _extract_planning_entities(self, message: str) -> Dict:
        """提取行程规划实体"""
        import re
        entities = {
            'destination': self._extract_city(message),
            'days': 3,  # 默认3天
            'budget': 3000  # 默认预算
        }

        # 提取天数
        days_match = re.search(r'(\d+)[天日]', message)
        if days_match:
            entities['days'] = int(days_match.group(1))

        # 提取预算
        budget_match = re.search(r'预算(\d+)', message)
        if budget_match:
            entities['budget'] = int(budget_match.group(1))

        return entities

    def _extract_attraction_name(self, message: str) -> str:
        """提取景点名称"""
        attractions = ['迪士尼', '海洋公园', '故宫', '长城', '外滩']
        for attr in attractions:
            if attr in message:
                return attr
        return '景点'

    def _extract_flight_info(self, message: str) -> Dict:
        """提取航班信息"""
        import re
        entities = {}

        # 提取起止城市
        pattern = r'从(.+?)飞?[到往至](.+?)(?:[的，。]|$)'
        match = re.search(pattern, message)
        if match:
            entities['origin'] = match.group(1).strip()
            entities['destination'] = match.group(2).strip()

        # 提取日期
        date_match = re.search(r'(\d{1,2}月\d{1,2}[日号])', message)
        if date_match:
            entities['date'] = date_match.group(1)

        return entities

    def handle_flight_enhanced(self, entities: Dict) -> Dict:
        """增强版航班搜索"""
        origin = entities.get('origin', '北京')
        destination = entities.get('destination', '上海')
        date = entities.get('date', '待定')

        # 获取航班数据
        flights = self.tools.search_flights(origin, destination, date)

        # 确保数据格式正确
        for flight in flights:
            # 添加必要字段
            flight['departure_iata'] = flight.get('departure_iata', origin[:3].upper())
            flight['arrival_iata'] = flight.get('arrival_iata', destination[:3].upper())
            flight['carrier_code'] = flight.get('carrier_code', flight.get('airline', 'XX')[:2])
            flight['flight_number'] = flight.get('flight_number', flight.get('flight_no', '000'))
            flight['total_price'] = flight.get('total_price', flight.get('price', 0))
            flight['duration'] = flight.get('duration', '2h 30m')
            flight['cabin_class'] = flight.get('cabin_class', 'ECONOMY')
            flight['currency'] = 'CNY'

        content = f"""
### ✈️ {origin} → {destination} 航班查询

日期：{date}
找到 {len(flights)} 个航班：
"""

        for i, flight in enumerate(flights[:5], 1):
            content += f"""
**{i}. {flight['carrier_code']}{flight['flight_number']}**
- 时间：{flight.get('departure', 'N/A')} → {flight.get('arrival', 'N/A')}
- 时长：{flight['duration']}
- 价格：¥{flight['total_price']}
- 舱位：{flight['cabin_class']}
"""

        return {
            'action': 'search_flights',
            'content': content,
            'data': flights,
            'suggestions': [
                "建议提前预订获得优惠",
                "可以比较不同时间的票价",
                "注意查看行李额度"
            ],
            'requires_confirmation': False
        }

    def handle_original_intents(self, intent: IntentType, entities: Dict) -> Dict:
        """处理其他原有意图"""
        # 这里调用原有的处理方法
        if intent == IntentType.WEATHER:
            return self.handle_weather(entities)
        elif intent == IntentType.ATTRACTION:
            return self.handle_attractions(entities)
        elif intent == IntentType.RESTAURANT:
            return self.handle_restaurants(entities)
        else:
            return self.generate_general_response(entities)

    def handle_weather(self, entities: Dict) -> Dict:
        """天气查询"""
        city = entities.get('city', '北京')
        weather = self.tools.get_weather(city)

        if weather.get('success'):
            current = weather['current']
            content = f"""
### 🌤️ {city}天气

**当前：**
- 温度：{current['temperature']}°C
- 天气：{current['weather']}
- 湿度：{current['humidity']}%

**建议：**
- {'适合外出游玩' if int(current['temperature']) > 10 else '注意保暖'}
"""
            return {
                'action': 'get_weather',
                'content': content,
                'data': weather,
                'suggestions': [],
                'requires_confirmation': False
            }
        return self.generate_error_response("无法获取天气信息")

    def handle_attractions(self, entities: Dict) -> Dict:
        """景点查询"""
        city = entities.get('city', '北京')
        attractions = self.tools.search_attractions(city)

        content = f"### 🏛️ {city}景点推荐\n\n"
        for i, attr in enumerate(attractions[:5], 1):
            content += f"{i}. {attr['name']} - {attr.get('type', '景点')}\n"

        return {
            'action': 'search_attractions',
            'content': content,
            'data': attractions,
            'suggestions': ["可以根据兴趣选择景点"],
            'requires_confirmation': False
        }

    def handle_restaurants(self, entities: Dict) -> Dict:
        """餐厅查询"""
        city = entities.get('city', '北京')
        restaurants = self.tools.search_restaurants(city)

        content = f"### 🍴 {city}美食推荐\n\n"
        for i, rest in enumerate(restaurants[:5], 1):
            content += f"{i}. {rest['name']} - {rest.get('cuisine', '特色菜')}\n"

        return {
            'action': 'search_restaurants',
            'content': content,
            'data': restaurants,
            'suggestions': ["建议提前预订热门餐厅"],
            'requires_confirmation': False
        }

    def generate_general_response(self, entities: Dict) -> Dict:
        """生成通用响应"""
        return {
            'action': 'suggestion',
            'content': "我理解您的需求，让我为您提供相关信息...",
            'data': None,
            'suggestions': [
                "可以告诉我更多细节",
                "我可以帮您查询航班、酒店、景点等"
            ],
            'requires_confirmation': False
        }

    def generate_error_response(self, error_msg: str) -> Dict:
        """生成错误响应"""
        return {
            'action': 'error',
            'content': f"抱歉，处理时遇到问题：{error_msg}",
            'data': None,
            'suggestions': ["请重新描述您的需求"],
            'requires_confirmation': False
        }


# ==================== 使用示例 ====================

if __name__ == "__main__":
    agent = TravelAgent()

    # 测试用例
    test_cases = [
        "从机场到市区酒店的最快路线是什么？",
        "我要预订北京朝阳区的酒店，需要有游泳池和健身房，预算2000元以内",
        "查询迪士尼乐园的门票价格和开放时间",
        "我想12月15-17日去杭州旅游，预算3000元，帮我规划整个行程，包括住宿、景点和交通",
        "查询11月30日从香港飞往上海的航班"
    ]

    for query in test_cases:
        print(f"\n{'='*60}")
        print(f"测试: {query}")
        result = agent.process(query)
        print(f"响应类型: {result['action']}")
        print(f"内容预览: {result['content'][:200]}...")
        if result.get('suggestions'):
            print(f"建议: {result['suggestions']}")
        print(f"需要确认: {result.get('requires_confirmation', False)}")