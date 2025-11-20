"""
改进版 TravelTools - 旅行工具类
修复航班数据问题，增强酒店筛选功能
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os
import requests


class TravelTools:
    """
    旅行工具类 - 提供各种旅行相关数据
    改进版特性：
    1. 修复航班数据结构
    2. 增强酒店筛选
    3. 门票信息查询
    4. 完整行程规划
    """

    def __init__(self):
        """初始化工具"""
        # 配置API密钥
        self.amap_key = os.getenv('AMAP_API_KEY', '33b713c72bf676bdbf300951b0f238ce')
        self.deepseek_key = os.getenv('DEEPSEEK_API_KEY', 'sk-08493e83ce83432ea0d142f39b794ddf')

        # 初始化数据
        self._init_mock_data()

        print("✅ 工具初始化完成")
        print(f"  高德API: {'✅ 已配置' if self.amap_key else '❌ 未配置'}")
        print(f"  DeepSeek: {'✅ 已配置' if self.deepseek_key else '❌ 未配置'}")

    def _init_mock_data(self):
        """初始化模拟数据"""
        # 酒店设施列表
        self.hotel_amenities = [
            'WiFi', '停车场', '游泳池', '健身房', '早餐',
            '商务中心', '洗衣服务', '餐厅', '酒吧', 'SPA',
            '24小时前台', '行李寄存', '无烟房', '儿童设施'
        ]

        # 航空公司
        self.airlines = [
            ('CA', '中国国航'), ('CZ', '南方航空'), ('MU', '东方航空'),
            ('HU', '海南航空'), ('ZH', '深圳航空'), ('FM', '上海航空'),
            ('3U', '四川航空'), ('MF', '厦门航空')
        ]

        # 机型
        self.aircraft_types = [
            'B737', 'B777', 'B787', 'A320', 'A330', 'A350'
        ]

        # 景点数据
        self.attractions_data = {
            '北京': [
                {'name': '故宫', 'type': '历史文化', 'rating': 4.9, 'price': 60},
                {'name': '长城', 'type': '历史文化', 'rating': 4.8, 'price': 40},
                {'name': '天坛', 'type': '历史文化', 'rating': 4.8, 'price': 35},
                {'name': '颐和园', 'type': '园林', 'rating': 4.7, 'price': 30},
                {'name': '北海公园', 'type': '园林', 'rating': 4.6, 'price': 10}
            ],
            '上海': [
                {'name': '迪士尼乐园', 'type': '主题乐园', 'rating': 4.7, 'price': 399},
                {'name': '东方明珠', 'type': '地标建筑', 'rating': 4.5, 'price': 180},
                {'name': '外滩', 'type': '风景区', 'rating': 4.8, 'price': 0},
                {'name': '豫园', 'type': '园林', 'rating': 4.4, 'price': 40},
                {'name': '海洋馆', 'type': '博物馆', 'rating': 4.6, 'price': 160}
            ]
        }

    def search_hotels(self, city: str, checkin_date: str, checkout_date: str,
                     requirements: List[str] = None) -> List[Dict]:
        """
        搜索酒店（增强版）

        Args:
            city: 城市名称
            checkin_date: 入住日期
            checkout_date: 退房日期
            requirements: 用户需求列表 ['停车场', '游泳池']

        Returns:
            酒店列表，包含详细信息
        """
        hotels = []

        # 尝试使用高德API
        if self.amap_key and city:
            amap_hotels = self._search_hotels_amap(city)
            hotels.extend(amap_hotels)

        # 生成补充数据
        if len(hotels) < 10:
            mock_hotels = self._generate_mock_hotels(city, 10 - len(hotels))
            hotels.extend(mock_hotels)

        # 增强数据字段
        for hotel in hotels:
            # 确保有必要字段
            hotel['checkin_date'] = checkin_date
            hotel['checkout_date'] = checkout_date

            # 计算晚数和总价
            nights = self._calculate_nights(checkin_date, checkout_date)
            hotel['nights'] = nights
            hotel['total_price'] = hotel.get('price', 500) * nights

            # 生成房型信息
            if 'room_types' not in hotel:
                hotel['room_types'] = self._generate_room_types(hotel.get('price', 500))

            # 确保有设施信息
            if 'amenities' not in hotel:
                hotel['amenities'] = random.sample(
                    self.hotel_amenities,
                    random.randint(5, 10)
                )

            # 添加详细描述
            if 'description' not in hotel:
                hotel['description'] = self._generate_hotel_description(hotel)

            # 添加政策信息
            hotel['policies'] = {
                'checkin_time': '14:00',
                'checkout_time': '12:00',
                'cancellation': '入住前24小时免费取消',
                'deposit': '需要押金'
            }

        # 根据需求筛选
        if requirements:
            hotels = self._filter_hotels_by_requirements(hotels, requirements)

        return hotels

    def _filter_hotels_by_requirements(self, hotels: List[Dict],
                                      requirements: List[str]) -> List[Dict]:
        """根据需求筛选酒店"""
        filtered = []

        for hotel in hotels:
            amenities = hotel.get('amenities', [])
            # 检查是否满足所有需求
            meets_requirements = True
            for req in requirements:
                # 模糊匹配
                found = False
                for amenity in amenities:
                    if req in amenity or amenity in req:
                        found = True
                        break
                if not found:
                    meets_requirements = False
                    break

            if meets_requirements:
                filtered.append(hotel)

        return filtered

    def search_flights(self, origin: str, destination: str,
                      departure_date: str, cabin_class: str = 'ECONOMY') -> List[Dict]:
        """
        搜索航班（修复版）

        Returns:
            规范的航班数据列表
        """
        flights = []

        # 生成模拟航班数据
        num_flights = random.randint(6, 12)
        base_time = datetime.now().replace(hour=6, minute=0)

        for i in range(num_flights):
            # 随机航空公司
            airline_code, airline_name = random.choice(self.airlines)
            flight_number = f"{airline_code}{random.randint(100, 999)}"

            # 出发时间（分布在一天内）
            departure_time = base_time + timedelta(hours=i*2 + random.randint(0, 1))

            # 飞行时间（1.5-4小时）
            flight_duration = timedelta(
                hours=random.randint(1, 3),
                minutes=random.choice([0, 15, 30, 45])
            )
            arrival_time = departure_time + flight_duration

            # 价格（根据舱位等级）
            base_price = random.randint(600, 2000)
            if cabin_class == 'BUSINESS':
                price = base_price * 3
            elif cabin_class == 'FIRST':
                price = base_price * 5
            else:
                price = base_price

            flight = {
                # 基础信息
                'carrier_code': airline_code,
                'carrier_name': airline_name,
                'flight_number': flight_number,

                # 机场信息
                'departure_iata': origin[:3].upper(),
                'arrival_iata': destination[:3].upper(),
                'departure_airport': f"{origin}机场",
                'arrival_airport': f"{destination}机场",

                # 时间信息（修复格式）
                'departure': departure_time.strftime("%H:%M"),
                'arrival': arrival_time.strftime("%H:%M"),
                'departure_time': departure_time.isoformat(),
                'arrival_time': arrival_time.isoformat(),
                'duration': f"{flight_duration.seconds//3600}h {(flight_duration.seconds%3600)//60}m",

                # 舱位和机型
                'cabin_class': cabin_class,
                'aircraft_code': random.choice(self.aircraft_types),

                # 价格信息
                'base_price': price,
                'total_price': price,
                'currency': 'CNY',

                # 其他信息
                'number_of_bookable_seats': random.randint(5, 30),
                'included_checked_bags': '1件23kg' if cabin_class == 'ECONOMY' else '2件32kg',
                'included_cabin_bags': '1件7kg',
                'last_ticketing_date': (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),

                # 航班状态
                'status': '正常',
                'on_time_rate': f"{random.randint(70, 95)}%"
            }

            flights.append(flight)

        # 按出发时间排序
        flights.sort(key=lambda x: x['departure_time'])

        return flights

    def get_weather(self, city: str) -> Dict:
        """获取天气信息"""
        try:
            # 如果有高德API，使用真实天气
            if self.amap_key:
                return self._get_weather_amap(city)
        except:
            pass

        # 模拟天气数据
        weather_conditions = ['晴', '多云', '阴', '小雨', '雾']

        return {
            'success': True,
            'city': city,
            'current': {
                'temperature': random.randint(10, 30),
                'weather': random.choice(weather_conditions),
                'humidity': random.randint(40, 80),
                'wind_speed': random.randint(1, 5),
                'feels_like': random.randint(8, 32)
            },
            'forecast': [
                {
                    'date': (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d"),
                    'day_weather': random.choice(weather_conditions),
                    'night_weather': random.choice(weather_conditions),
                    'day_temp': random.randint(15, 30),
                    'night_temp': random.randint(10, 20)
                }
                for i in range(1, 4)
            ]
        }

    def search_attractions(self, city: str) -> List[Dict]:
        """搜索景点"""
        attractions = []

        # 使用预定义数据
        if city in self.attractions_data:
            attractions = self.attractions_data[city].copy()
        else:
            # 生成通用景点
            attractions = self._generate_mock_attractions(city)

        # 增强景点信息
        for attr in attractions:
            # 添加详细信息
            if 'address' not in attr:
                attr['address'] = f"{city}市中心"

            if 'opening_hours' not in attr:
                attr['opening_hours'] = '09:00-18:00'

            if 'description' not in attr:
                attr['description'] = self._generate_attraction_description(attr)

            if 'tips' not in attr:
                attr['tips'] = [
                    "建议预订门票避免排队",
                    "最佳游览时间2-3小时",
                    "适合拍照的景点"
                ]

        return attractions

    def get_ticket_info(self, attraction_name: str) -> Dict:
        """
        获取门票信息

        Returns:
            包含票价、开放时间、优惠政策等
        """
        # 特定景点信息
        ticket_info = {
            '迪士尼': {
                'name': '上海迪士尼乐园',
                'regular_price': 435,
                'peak_price': 659,
                'child_price': 325,
                'opening_hours': '09:00-21:00',
                'tips': [
                    "建议提前在线购票",
                    "可购买快速通行证",
                    "儿童、老人有优惠"
                ],
                'packages': [
                    {'name': '一日票', 'price': 435},
                    {'name': '两日票', 'price': 780},
                    {'name': '年卡', 'price': 1650}
                ]
            },
            '海洋公园': {
                'name': '香港海洋公园',
                'adult_price': 498,
                'child_price': 249,
                'opening_hours': '10:00-18:00',
                'tips': [
                    "网上购票有9折优惠",
                    "可以购买餐券套票",
                    "3岁以下免费"
                ],
                'packages': [
                    {'name': '标准票', 'price': 498},
                    {'name': '快速通行证', 'price': 280},
                    {'name': '全包套票', 'price': 799}
                ]
            }
        }

        # 查找匹配的景点
        for key, info in ticket_info.items():
            if key in attraction_name:
                return {
                    'success': True,
                    'data': info
                }

        # 生成通用门票信息
        return {
            'success': True,
            'data': {
                'name': attraction_name,
                'adult_price': random.randint(30, 200),
                'child_price': random.randint(15, 100),
                'opening_hours': '09:00-18:00',
                'tips': [
                    "建议提前预订",
                    "周末人较多",
                    "学生证有优惠"
                ]
            }
        }

    def search_restaurants(self, city: str) -> List[Dict]:
        """搜索餐厅"""
        cuisines = ['川菜', '粤菜', '江浙菜', '西餐', '日料', '韩餐', '火锅', '烧烤']
        restaurants = []

        for i in range(10):
            restaurant = {
                'name': f"{city}美食{i+1}号",
                'cuisine': random.choice(cuisines),
                'rating': round(random.uniform(4.0, 5.0), 1),
                'price_per_person': random.randint(50, 300),
                'address': f"{city}市美食街{i+1}号",
                'popular_dishes': [
                    f"招牌菜{j+1}" for j in range(3)
                ],
                'opening_hours': '11:00-22:00',
                'need_reservation': random.choice([True, False])
            }
            restaurants.append(restaurant)

        return restaurants

    def plan_itinerary(self, destination: str, days: int, budget: float,
                      interests: List[str]) -> Dict:
        """
        规划完整行程

        Returns:
            包含每日安排、预算分配、推荐项目的完整行程
        """
        # 获取基础数据
        hotels = self.search_hotels(destination, '', '')[:3]
        attractions = self.search_attractions(destination)
        restaurants = self.search_restaurants(destination)

        # 预算分配
        budget_allocation = {
            'accommodation': budget * 0.3,
            'transportation': budget * 0.2,
            'attractions': budget * 0.2,
            'dining': budget * 0.2,
            'shopping': budget * 0.1
        }

        # 生成每日行程
        daily_plans = []
        for day in range(1, days + 1):
            # 选择当天的景点
            day_attractions = random.sample(
                attractions,
                min(3, len(attractions))
            )

            # 选择餐厅
            day_restaurants = random.sample(
                restaurants,
                min(2, len(restaurants))
            )

            daily_plan = {
                'day': day,
                'date': (datetime.now() + timedelta(days=day-1)).strftime("%Y-%m-%d"),
                'morning': [
                    f"08:00 - 酒店早餐",
                    f"09:00 - 前往{day_attractions[0]['name']}",
                    f"09:30 - 游览{day_attractions[0]['name']}"
                ],
                'afternoon': [
                    f"12:00 - 午餐：{day_restaurants[0]['name']}",
                    f"14:00 - 前往{day_attractions[1]['name'] if len(day_attractions) > 1 else '市中心'}",
                    f"14:30 - 游览/购物"
                ],
                'evening': [
                    f"18:00 - 晚餐：{day_restaurants[1]['name'] if len(day_restaurants) > 1 else '当地特色'}",
                    f"20:00 - 返回酒店休息"
                ],
                'estimated_cost': budget / days,
                'tips': [
                    "记得带好相机",
                    "穿舒适的鞋子",
                    "注意防晒"
                ]
            }
            daily_plans.append(daily_plan)

        # 生成完整行程
        itinerary = {
            'destination': destination,
            'days': days,
            'total_budget': budget,
            'budget_allocation': budget_allocation,
            'daily_plans': daily_plans,
            'recommended_hotels': hotels[:3],
            'must_visit': attractions[:5],
            'estimated_cost': budget * 0.9,
            'recommendations': [
                f"建议提前预订{hotels[0]['name']}",
                f"必去景点：{attractions[0]['name']}",
                "记得品尝当地特色美食",
                "建议购买城市旅游卡"
            ]
        }

        return itinerary

    # ==================== 辅助方法 ====================

    def _calculate_nights(self, checkin: str, checkout: str) -> int:
        """计算住宿晚数"""
        try:
            if checkin and checkout:
                start = datetime.strptime(checkin, "%Y-%m-%d")
                end = datetime.strptime(checkout, "%Y-%m-%d")
                return max((end - start).days, 1)
        except:
            pass
        return 1

    def _generate_room_types(self, base_price: float) -> List[Dict]:
        """生成房型信息"""
        return [
            {
                'name': '标准双床房',
                'price': base_price,
                'beds': '2张单人床',
                'size': '25平米',
                'max_occupancy': 2
            },
            {
                'name': '豪华大床房',
                'price': base_price * 1.2,
                'beds': '1张大床',
                'size': '30平米',
                'max_occupancy': 2
            },
            {
                'name': '行政套房',
                'price': base_price * 1.8,
                'beds': '1张大床+沙发床',
                'size': '45平米',
                'max_occupancy': 3
            }
        ]

    def _generate_hotel_description(self, hotel: Dict) -> str:
        """生成酒店描述"""
        templates = [
            f"{hotel['name']}位于{hotel.get('city', '市')}中心，提供优质的住宿体验。",
            f"现代化的{hotel['name']}，地理位置优越，设施完善。",
            f"{hotel['name']}致力于为客人提供舒适、便捷的入住体验。"
        ]
        return random.choice(templates)

    def _generate_attraction_description(self, attraction: Dict) -> str:
        """生成景点描述"""
        return f"{attraction['name']}是当地著名的{attraction.get('type', '景点')}，深受游客喜爱。"

    def _generate_mock_hotels(self, city: str, count: int) -> List[Dict]:
        """生成模拟酒店数据"""
        hotels = []
        hotel_types = ['商务酒店', '度假酒店', '精品酒店', '经济型酒店', '豪华酒店']

        for i in range(count):
            price = random.randint(200, 1500)
            hotel = {
                'name': f"{city}酒店{i+1}号",
                'type': random.choice(hotel_types),
                'address': f"{city}市中心街道{i+1}号",
                'city': city,
                'rating': round(random.uniform(4.0, 5.0), 1),
                'price': price,
                'amenities': random.sample(self.hotel_amenities, random.randint(5, 10)),
                'tel': f"021-{''.join([str(random.randint(0, 9)) for _ in range(8)])}"
            }
            hotels.append(hotel)

        return hotels

    def _generate_mock_attractions(self, city: str) -> List[Dict]:
        """生成模拟景点数据"""
        attraction_types = ['历史文化', '自然风光', '主题乐园', '博物馆', '地标建筑']
        attractions = []

        for i in range(5):
            attraction = {
                'name': f"{city}景点{i+1}",
                'type': random.choice(attraction_types),
                'rating': round(random.uniform(4.0, 5.0), 1),
                'price': random.randint(0, 200),
                'address': f"{city}市景区{i+1}号"
            }
            attractions.append(attraction)

        return attractions

    def _search_hotels_amap(self, city: str) -> List[Dict]:
        """使用高德地图API搜索酒店"""
        try:
            url = "https://restapi.amap.com/v3/place/text"
            params = {
                'key': self.amap_key,
                'keywords': '酒店',
                'city': city,
                'types': '100100',  # 酒店类型
                'offset': 20
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                hotels = []

                for poi in data.get('pois', []):
                    hotel = {
                        'name': poi['name'],
                        'address': poi.get('address', ''),
                        'tel': poi.get('tel', ''),
                        'location': poi.get('location', ''),
                        'city': city,
                        'rating': round(random.uniform(4.0, 5.0), 1),
                        'price': random.randint(200, 1500)
                    }
                    hotels.append(hotel)

                return hotels
        except Exception as e:
            print(f"高德API调用失败: {e}")

        return []

    def _get_weather_amap(self, city: str) -> Dict:
        """使用高德地图API获取天气"""
        try:
            url = "https://restapi.amap.com/v3/weather/weatherInfo"
            params = {
                'key': self.amap_key,
                'city': city,
                'extensions': 'all'
            }

            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['status'] == '1' and data.get('forecasts'):
                    forecast = data['forecasts'][0]
                    current = forecast['casts'][0] if forecast.get('casts') else {}

                    return {
                        'success': True,
                        'city': forecast['city'],
                        'current': {
                            'temperature': current.get('daytemp', 20),
                            'weather': current.get('dayweather', '晴'),
                            'humidity': random.randint(40, 80),
                            'wind_speed': current.get('daypower', '≤3')
                        },
                        'forecast': [
                            {
                                'date': cast['date'],
                                'day_weather': cast['dayweather'],
                                'night_weather': cast['nightweather'],
                                'day_temp': cast['daytemp'],
                                'night_temp': cast['nighttemp']
                            }
                            for cast in forecast.get('casts', [])[:3]
                        ]
                    }
        except Exception as e:
            print(f"天气API调用失败: {e}")

        return self.get_weather(city)  # 降级到模拟数据


# 测试
if __name__ == "__main__":
    tools = TravelTools()

    # 测试酒店搜索
    print("\n测试酒店搜索（带筛选）:")
    hotels = tools.search_hotels(
        city="北京",
        checkin_date="2025-12-01",
        checkout_date="2025-12-03",
        requirements=["停车场", "游泳池"]
    )
    print(f"找到 {len(hotels)} 家符合条件的酒店")
    if hotels:
        print(f"第一家: {hotels[0]['name']}")
        print(f"  设施: {hotels[0]['amenities']}")

    # 测试航班搜索
    print("\n测试航班搜索:")
    flights = tools.search_flights("北京", "上海", "2025-12-01")
    print(f"找到 {len(flights)} 个航班")
    if flights:
        flight = flights[0]
        print(f"第一个航班: {flight['carrier_code']}{flight['flight_number']}")
        print(f"  时间: {flight['departure']} -> {flight['arrival']}")
        print(f"  价格: ¥{flight['total_price']}")

    # 测试门票查询
    print("\n测试门票查询:")
    ticket = tools.get_ticket_info("迪士尼")
    if ticket['success']:
        info = ticket['data']
        print(f"{info['name']}: ¥{info.get('regular_price', info.get('adult_price'))}")
        print(f"开放时间: {info['opening_hours']}")

    # 测试行程规划
    print("\n测试行程规划:")
    itinerary = tools.plan_itinerary("上海", 3, 5000, ["文化", "美食"])
    print(f"目的地: {itinerary['destination']}")
    print(f"天数: {itinerary['days']}天")
    print(f"第一天行程:")
    for activity in itinerary['daily_plans'][0]['morning']:
        print(f"  {activity}")