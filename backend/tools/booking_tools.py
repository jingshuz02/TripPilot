"""
预订工具 - 封装Amadeus API
为Agent提供简单的预订接口

"""
from backend.booking import AmadeusService
from config.config import Config


class BookingTool:
    """
    预订工具类
    封装航班和酒店搜索功能，提供给Agent使用
    """

    def __init__(self):
        """初始化预订工具"""
        # 初始化DeepSeek客户端（用于AI增强）
        self.deepseek_client = Config.get_deepseek_client()

        # 创建Amadeus服务
        self.amadeus = AmadeusService(self.deepseek_client)

        print("✅ 预订工具初始化完成")

    # ==================== 航班搜索 ====================

    def search_flights(self, origin: str, destination: str, date: str, **kwargs) -> dict:
        """
        搜索航班

        Args:
            origin: 出发地IATA代码（如'HKG'）
            destination: 目的地IATA代码（如'NRT'）
            date: 出发日期（YYYY-MM-DD格式）
            **kwargs: 其他可选参数
                - adults: 成人数量，默认1
                - travel_class: 舱位（ECONOMY/BUSINESS/FIRST），默认ECONOMY
                - non_stop: 是否只要直飞，默认True
                - max_results: 最多返回几个结果，默认10

        Returns:
            {
                'success': True/False,
                'data': [...],      # 航班列表
                'count': 5,         # 找到的航班数
                'message': '找到5个航班'
            }

        Example:
            >>> tool = BookingTool()
            >>> result = tool.search_flights('HKG', 'NRT', '2025-12-01')
            >>> if result['success']:
            >>>     print(f"找到 {result['count']} 个航班")
            >>>     for flight in result['data']:
            >>>         print(f"价格: ${flight['price']['total']}")
        """
        params = {
            'origin': origin,
            'destination': destination,
            'departure_date': date,
            'adults': kwargs.get('adults', 1),
            'travel_class': kwargs.get('travel_class', 'ECONOMY'),
            'non_stop': kwargs.get('non_stop', True),
            'max_results': kwargs.get('max_results', 10)
        }

        return self.amadeus.search_flights(params)

    # ==================== 酒店搜索 ====================

    def search_hotels(self, latitude: float, longitude: float,
                     check_in: str, check_out: str, **kwargs) -> dict:
        """
        搜索酒店（通过经纬度）

        Args:
            latitude: 纬度
            longitude: 经度
            check_in: 入住日期（YYYY-MM-DD格式）
            check_out: 退房日期（YYYY-MM-DD格式）
            **kwargs: 其他可选参数
                - radius: 搜索半径（公里），默认5
                - adults: 成人数量，默认2

        Returns:
            {
                'success': True/False,
                'hotels': [...],        # 酒店基本信息
                'offers': [...],        # 房间报价
                'reviews': [...],       # 酒店评价
                'count': 12,            # 找到的酒店数
                'ai_enhanced': True,    # 是否使用了AI增强
                'message': '找到12个酒店'
            }

        Example:
            >>> tool = BookingTool()
            >>> result = tool.search_hotels(
            ...     latitude=35.6762,
            ...     longitude=139.6503,
            ...     check_in='2025-12-01',
            ...     check_out='2025-12-05'
            ... )
            >>> if result['success']:
            >>>     print(result['message'])
            >>>     for hotel in result['hotels']:
            >>>         print(f"酒店: {hotel['name']}")
        """
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'check_in_date': check_in,
            'check_out_date': check_out,
            'radius': kwargs.get('radius', 5),
            'adults': kwargs.get('adults', 2)
        }

        return self.amadeus.search_hotels(params)

    def search_hotels_by_city(self, city: str, check_in: str, check_out: str, **kwargs) -> dict:
        """
        搜索酒店（通过城市名）

        Args:
            city: 城市名（中文或英文，如'东京'或'Tokyo'）
            check_in: 入住日期（YYYY-MM-DD格式）
            check_out: 退房日期（YYYY-MM-DD格式）
            **kwargs: 其他可选参数（同search_hotels）

        Returns:
            同search_hotels的返回格式

        Example:
            >>> tool = BookingTool()
            >>> result = tool.search_hotels_by_city('东京', '2025-12-01', '2025-12-05')
        """
        # 城市坐标映射表
        CITY_COORDS = {
            # 日本
            '东京': (35.6762, 139.6503),
            'Tokyo': (35.6762, 139.6503),
            '大阪': (34.6937, 135.5023),
            'Osaka': (34.6937, 135.5023),
            '京都': (35.0116, 135.7681),
            'Kyoto': (35.0116, 135.7681),

            # 中国
            '北京': (39.9042, 116.4074),
            'Beijing': (39.9042, 116.4074),
            '上海': (31.2304, 121.4737),
            'Shanghai': (31.2304, 121.4737),
            '香港': (22.3193, 114.1694),
            'Hong Kong': (22.3193, 114.1694),
            '广州': (23.1291, 113.2644),
            'Guangzhou': (23.1291, 113.2644),
            '深圳': (22.5431, 114.0579),
            'Shenzhen': (22.5431, 114.0579),

            # 其他热门城市
            '新加坡': (1.3521, 103.8198),
            'Singapore': (1.3521, 103.8198),
            '曼谷': (13.7563, 100.5018),
            'Bangkok': (13.7563, 100.5018),
            '首尔': (37.5665, 126.9780),
            'Seoul': (37.5665, 126.9780),

            # 可以继续添加更多城市...
        }

        if city in CITY_COORDS:
            lat, lon = CITY_COORDS[city]
            return self.search_hotels(lat, lon, check_in, check_out, **kwargs)
        else:
            return {
                'success': False,
                'hotels': [],
                'offers': [],
                'reviews': [],
                'count': 0,
                'ai_enhanced': False,
                'message': f"未找到城市'{city}'的坐标，请使用经纬度搜索或添加该城市"
            }

    # ==================== 便捷方法 ====================

    def get_flight_price(self, origin: str, destination: str, date: str) -> dict:
        """
        快速获取航班价格（只返回最便宜的）

        Returns:
            {
                'success': True/False,
                'cheapest_price': 500.00,
                'currency': 'USD',
                'message': '最低价格: $500.00'
            }
        """
        result = self.search_flights(origin, destination, date, max_results=5)

        if result['success'] and result['data']:
            prices = [float(f['price']['total']) for f in result['data'] if 'price' in f]
            if prices:
                cheapest = min(prices)
                return {
                    'success': True,
                    'cheapest_price': cheapest,
                    'currency': 'USD',
                    'message': f"最低价格: ${cheapest:.2f}"
                }

        return {
            'success': False,
            'cheapest_price': None,
            'currency': 'USD',
            'message': '未找到价格信息'
        }

    def get_hotel_count(self, city: str) -> dict:
        """
        快速获取某城市的酒店数量

        Returns:
            {
                'success': True/False,
                'count': 12,
                'message': '找到12个酒店'
            }
        """
        from datetime import date, timedelta

        # 使用明天作为入住日期
        tomorrow = (date.today() + timedelta(days=1)).strftime('%Y-%m-%d')
        checkout = (date.today() + timedelta(days=2)).strftime('%Y-%m-%d')

        result = self.search_hotels_by_city(city, tomorrow, checkout)

        return {
            'success': result['success'],
            'count': result['count'],
            'message': result['message']
        }