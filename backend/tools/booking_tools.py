"""
预订工具 - 航班、酒店搜索和预订
注: 目前使用模拟数据，等待Amadeus API集成
"""
from datetime import datetime, timedelta
import random
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class BookingTool:
    """预订工具类 - 航班和酒店"""

    def __init__(self, base_url="http://localhost:5000"):
        """
        初始化预订工具

        Args:
            base_url: Flask后端地址
        """
        self.base_url = base_url

        # 模拟航空公司
        self.airlines = ["国航", "东航", "南航", "日航", "全日空", "港龙航空"]

        # 模拟酒店数据
        self.mock_hotels = {
            "东京": [
                {
                    "name": "东京帝国酒店",
                    "rating": 4.8,
                    "price_per_night": 2500,
                    "amenities": ["免费WiFi", "健身房", "游泳池", "餐厅"],
                    "location": "银座",
                    "description": "位于市中心的豪华酒店"
                },
                {
                    "name": "浅草寺商务酒店",
                    "rating": 4.3,
                    "price_per_night": 800,
                    "amenities": ["免费WiFi", "早餐"],
                    "location": "浅草",
                    "description": "性价比高，靠近浅草寺"
                },
                {
                    "name": "新宿现代酒店",
                    "rating": 4.5,
                    "price_per_night": 1200,
                    "amenities": ["免费WiFi", "健身房", "餐厅"],
                    "location": "新宿",
                    "description": "交通便利，购物方便"
                }
            ],
            "北京": [
                {
                    "name": "北京王府半岛酒店",
                    "rating": 4.9,
                    "price_per_night": 2000,
                    "amenities": ["免费WiFi", "健身房", "游泳池", "餐厅", "水疗"],
                    "location": "王府井",
                    "description": "豪华五星级酒店"
                },
                {
                    "name": "如家快捷酒店",
                    "rating": 4.0,
                    "price_per_night": 300,
                    "amenities": ["免费WiFi"],
                    "location": "国贸",
                    "description": "经济型连锁酒店"
                }
            ]
        }

    def search_flights(self, origin: str, destination: str, date: str,
                      passengers: int = 1) -> list:
        """
        搜索航班

        Args:
            origin: 出发地（城市名或机场代码）
            destination: 目的地
            date: 出发日期 (YYYY-MM-DD)
            passengers: 乘客数量

        Returns:
            航班列表
        """
        # TODO: 等待Junjie实现Amadeus API后替换

        # 生成3-5个模拟航班
        flights = []
        num_flights = random.randint(3, 5)

        for i in range(num_flights):
            # 随机生成时间
            hour = random.randint(6, 22)
            minute = random.choice([0, 30])
            departure_time = f"{hour:02d}:{minute:02d}"

            # 随机飞行时长（2-6小时）
            duration = random.randint(120, 360)
            arrival_hour = (hour + duration // 60) % 24
            arrival_minute = (minute + duration % 60) % 60
            arrival_time = f"{arrival_hour:02d}:{arrival_minute:02d}"

            # 随机价格
            base_price = random.randint(800, 3000)

            flight = {
                'id': f'FL{random.randint(1000, 9999)}',
                'airline': random.choice(self.airlines),
                'flight_number': f'{random.choice(["CA", "MU", "CZ", "JL", "NH"])}{random.randint(100, 999)}',
                'origin': origin,
                'destination': destination,
                'date': date,
                'departure_time': departure_time,
                'arrival_time': arrival_time,
                'duration': f'{duration // 60}小时{duration % 60}分钟',
                'price': base_price * passengers,
                'currency': 'CNY',
                'seats_available': random.randint(5, 50),
                'class': 'Economy'
            }

            flights.append(flight)

        # 按价格排序
        flights.sort(key=lambda x: x['price'])

        return flights

    def search_hotels(self, city: str, check_in: str, check_out: str,
                     budget: float = None) -> list:
        """
        搜索酒店

        Args:
            city: 城市名称
            check_in: 入住日期 (YYYY-MM-DD)
            check_out: 退房日期 (YYYY-MM-DD)
            budget: 预算（每晚，可选）

        Returns:
            酒店列表
        """
        # TODO: 等待Junjie实现Amadeus API后替换

        hotels = []

        # 尝试从模拟数据中查找
        mock_data = []
        for key in self.mock_hotels.keys():
            if key in city or city in key:
                mock_data = self.mock_hotels[key]
                break

        # 如果没找到，生成默认数据
        if not mock_data:
            mock_data = [
                {
                    "name": f"{city}中心酒店",
                    "rating": 4.0,
                    "price_per_night": 800,
                    "amenities": ["免费WiFi", "早餐"],
                    "location": "市中心",
                    "description": f"位于{city}的酒店"
                }
            ]

        # 计算住宿天数
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d")
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d")
            nights = (check_out_date - check_in_date).days
        except:
            nights = 1

        # 处理每个酒店
        for i, hotel in enumerate(mock_data):
            price_per_night = hotel['price_per_night']

            # 如果有预算限制，跳过超预算的
            if budget and price_per_night > budget:
                continue

            total_price = price_per_night * nights

            hotels.append({
                'id': f'HT{random.randint(1000, 9999)}',
                'name': hotel['name'],
                'rating': hotel['rating'],
                'price_per_night': price_per_night,
                'total_price': total_price,
                'nights': nights,
                'amenities': hotel['amenities'],
                'location': hotel['location'],
                'description': hotel['description'],
                'check_in': check_in,
                'check_out': check_out,
                'available_rooms': random.randint(1, 10)
            })

        # 按价格排序
        hotels.sort(key=lambda x: x['price_per_night'])

        return hotels

    def book_flight(self, flight_id: str, passengers: int = 1) -> dict:
        """
        预订航班

        Args:
            flight_id: 航班ID
            passengers: 乘客数量

        Returns:
            预订结果
        """
        # TODO: 实现真实预订逻辑
        return {
            'success': True,
            'booking_id': f'BK{random.randint(10000, 99999)}',
            'flight_id': flight_id,
            'status': 'confirmed',
            'message': '航班预订成功！预订号: BK' + str(random.randint(10000, 99999))
        }

    def book_hotel(self, hotel_id: str, rooms: int = 1) -> dict:
        """
        预订酒店

        Args:
            hotel_id: 酒店ID
            rooms: 房间数量

        Returns:
            预订结果
        """
        # TODO: 实现真实预订逻辑
        return {
            'success': True,
            'booking_id': f'BK{random.randint(10000, 99999)}',
            'hotel_id': hotel_id,
            'status': 'confirmed',
            'message': '酒店预订成功！预订号: BK' + str(random.randint(10000, 99999))
        }


# 测试代码
if __name__ == "__main__":
    tool = BookingTool()

    print("=" * 50)
    print("测试预订工具")
    print("=" * 50)

    # 测试航班搜索
    print("\n1. 搜索航班（北京 → 东京）:")
    flights = tool.search_flights("北京", "东京", "2024-12-01", passengers=1)
    for flight in flights[:3]:
        print(f"  ✈️  {flight['airline']} {flight['flight_number']}")
        print(f"     {flight['departure_time']} → {flight['arrival_time']}")
        print(f"     价格: ¥{flight['price']}\n")

    # 测试酒店搜索
    print("2. 搜索酒店（东京，3晚）:")
    hotels = tool.search_hotels("东京", "2024-12-01", "2024-12-04")
    for hotel in hotels[:3]:
        print(f"  🏨 {hotel['name']}")
        print(f"     评分: {hotel['rating']}/5.0")
        print(f"     价格: ¥{hotel['price_per_night']}/晚 (共¥{hotel['total_price']})")
        print(f"     设施: {', '.join(hotel['amenities'])}\n")