# """
# TripPilot 配置文件
# 包含所有API密钥和系统配置
# """
# import os
# from openai import OpenAI


# class Config:
#     """系统配置类"""

#     # ==================== API密钥配置 ====================

#     # 高德地图API（已配置）
#     GAODE_API_KEY = "33b713c72bf676bdbf300951b0f238ce"

#     # DeepSeek API（需要你自己的密钥）
#     DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-08493e83ce83432ea0d142f39b794ddf')
#     DEEPSEEK_BASE_URL = "https://api.deepseek.com"
#     DEEPSEEK_MODEL = "deepseek-chat"

#     # Amadeus API（可选，用于真实航班/酒店数据）
#     # 注意：这是测试环境，数据有限！生产环境需要付费
#     AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID', '6VI59RCfSUaykDxeRa5GSO6arTqdAqGl')
#     AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET', 'gAiUpG7C6UJbsndp')
#     AMADEUS_TEST_MODE = True  # True=测试环境(免费但数据少), False=生产环境(付费)

#     # ==================== 系统配置 ====================

#     # 是否使用模拟数据（当API失败时）
#     USE_MOCK_DATA_ON_FAILURE = True

#     # 是否优先使用AI生成（推荐）
#     PREFER_AI_GENERATION = True

#     # Flask后端配置
#     FLASK_BACKEND_URL = "http://localhost:5000"

#     # ==================== 城市坐标映射 ====================
#     CITY_COORDINATES = {
#         # 中国城市
#         '北京': (39.9042, 116.4074),
#         '上海': (31.2304, 121.4737),
#         '广州': (23.1291, 113.2644),
#         '深圳': (22.5431, 114.0579),
#         '香港': (22.3193, 114.1694),
#         '成都': (30.5728, 104.0668),
#         '杭州': (30.2741, 120.1551),
#         '西安': (34.3416, 108.9398),
#         '武汉': (30.5928, 114.3055),
#         '重庆': (29.5630, 106.5516),

#         # 日本城市
#         '东京': (35.6762, 139.6503),
#         'Tokyo': (35.6762, 139.6503),
#         '大阪': (34.6937, 135.5023),
#         'Osaka': (34.6937, 135.5023),
#         '京都': (35.0116, 135.7681),
#         'Kyoto': (35.0116, 135.7681),
#         '名古屋': (35.1815, 136.9066),
#         '札幌': (43.0642, 141.3469),
#         '福冈': (33.5904, 130.4017),

#         # 韩国城市
#         '首尔': (37.5665, 126.9780),
#         'Seoul': (37.5665, 126.9780),
#         '釜山': (35.1796, 129.0756),

#         # 东南亚城市
#         '新加坡': (1.3521, 103.8198),
#         'Singapore': (1.3521, 103.8198),
#         '曼谷': (13.7563, 100.5018),
#         'Bangkok': (13.7563, 100.5018),
#         '吉隆坡': (3.1390, 101.6869),
#         '巴厘岛': (-8.4095, 115.1889),

#         # 欧美城市
#         '纽约': (40.7128, -74.0060),
#         'New York': (40.7128, -74.0060),
#         '伦敦': (51.5074, -0.1278),
#         'London': (51.5074, -0.1278),
#         '巴黎': (48.8566, 2.3522),
#         'Paris': (48.8566, 2.3522),
#         '洛杉矶': (34.0522, -118.2437),
#         '旧金山': (37.7749, -122.4194),
#     }

#     # ==================== 机场代码映射 ====================
#     AIRPORT_CODES = {
#         # 中国机场
#         '北京': 'PEK',
#         '北京首都': 'PEK',
#         '北京大兴': 'PKX',
#         '上海': 'PVG',
#         '上海浦东': 'PVG',
#         '上海虹桥': 'SHA',
#         '广州': 'CAN',
#         '深圳': 'SZX',
#         '香港': 'HKG',
#         '成都': 'CTU',
#         '杭州': 'HGH',
#         '西安': 'XIY',
#         '武汉': 'WUH',
#         '重庆': 'CKG',

#         # 日本机场
#         '东京': 'NRT',
#         'Tokyo': 'NRT',
#         '东京成田': 'NRT',
#         '东京羽田': 'HND',
#         '大阪': 'KIX',
#         'Osaka': 'KIX',
#         '大阪关西': 'KIX',
#         '京都': 'KIX',  # 京都用大阪机场
#         '名古屋': 'NGO',

#         # 其他亚洲机场
#         '首尔': 'ICN',
#         'Seoul': 'ICN',
#         '新加坡': 'SIN',
#         'Singapore': 'SIN',
#         '曼谷': 'BKK',
#         'Bangkok': 'BKK',

#         # 欧美机场
#         '纽约': 'JFK',
#         'New York': 'JFK',
#         '伦敦': 'LHR',
#         'London': 'LHR',
#         '巴黎': 'CDG',
#         'Paris': 'CDG',
#         '洛杉矶': 'LAX',
#         '旧金山': 'SFO',
#     }

#     @classmethod
#     def get_deepseek_client(cls):
#         """获取DeepSeek客户端"""
#         return OpenAI(
#             api_key=cls.DEEPSEEK_API_KEY,
#             base_url=cls.DEEPSEEK_BASE_URL
#         )

#     @classmethod
#     def get_city_coordinates(cls, city: str) -> tuple:
#         """获取城市坐标"""
#         return cls.CITY_COORDINATES.get(city, (39.9042, 116.4074))  # 默认北京

#     @classmethod
#     def get_airport_code(cls, city: str) -> str:
#         """获取机场代码"""
#         return cls.AIRPORT_CODES.get(city, 'PEK')  # 默认北京首都机场



"""
TripPilot Configuration File
Contains all API keys and system configurations
"""
import os
from openai import OpenAI


class Config:
    """System Configuration Class"""

    # ==================== API Key Configuration ====================

    # Gaode Maps API (Configured)
    GAODE_API_KEY = "33b713c72bf676bdbf300951b0f238ce"

    # DeepSeek API (Requires your own key)
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', 'sk-08493e83ce83432ea0d142f39b794ddf')
    DEEPSEEK_BASE_URL = "https://api.deepseek.com"
    DEEPSEEK_MODEL = "deepseek-chat"

    # Amadeus API (Optional, for real flight/hotel data)
    # Note: This is the test environment, data is limited! Production environment requires payment.
    AMADEUS_CLIENT_ID = os.getenv('AMADEUS_CLIENT_ID', '6VI59RCfSUaykDxeRa5GSO6arTqdAqGl')
    AMADEUS_CLIENT_SECRET = os.getenv('AMADEUS_CLIENT_SECRET', 'gAiUpG7C6UJbsndp')
    AMADEUS_TEST_MODE = True  # True=Test environment (Free but limited data), False=Production environment (Paid)

    # ==================== System Configuration ====================

    # Whether to use mock data (when API fails)
    USE_MOCK_DATA_ON_FAILURE = True

    # Whether to prioritize AI generation (Recommended)
    PREFER_AI_GENERATION = True

    # Flask Backend Configuration
    FLASK_BACKEND_URL = "http://localhost:5000"

    # ==================== City Coordinates Mapping ====================
    CITY_COORDINATES = {
        # Chinese Cities
        '北京': (39.9042, 116.4074),
        'Shanghai': (31.2304, 121.4737),
        'Guangzhou': (23.1291, 113.2644),
        'Shenzhen': (22.5431, 114.0579),
        'Hong Kong': (22.3193, 114.1694),
        'Chengdu': (30.5728, 104.0668),
        'Hangzhou': (30.2741, 120.1551),
        'Xi\'an': (34.3416, 108.9398),
        'Wuhan': (30.5928, 114.3055),
        'Chongqing': (29.5630, 106.5516),

        # Japanese Cities
        'Tokyo': (35.6762, 139.6503),
        'Osaka': (34.6937, 135.5023),
        'Kyoto': (35.0116, 135.7681),
        'Nagoya': (35.1815, 136.9066),
        'Sapporo': (43.0642, 141.3469),
        'Fukuoka': (33.5904, 130.4017),

        # Korean Cities
        'Seoul': (37.5665, 126.9780),
        'Busan': (35.1796, 129.0756),

        # Southeast Asian Cities
        'Singapore': (1.3521, 103.8198),
        'Bangkok': (13.7563, 100.5018),
        'Kuala Lumpur': (3.1390, 101.6869),
        'Bali': (-8.4095, 115.1889),

        # European and American Cities
        'New York': (40.7128, -74.0060),
        'London': (51.5074, -0.1278),
        'Paris': (48.8566, 2.3522),
        'Los Angeles': (34.0522, -118.2437),
        'San Francisco': (37.7749, -122.4194),
    }

    # ==================== Airport Codes Mapping ====================
    AIRPORT_CODES = {
        # Chinese Airports
        'Beijing': 'PEK',
        'Beijing Capital': 'PEK',
        'Beijing Daxing': 'PKX',
        'Shanghai': 'PVG',
        'Shanghai Pudong': 'PVG',
        'Shanghai Hongqiao': 'SHA',
        'Guangzhou': 'CAN',
        'Shenzhen': 'SZX',
        'Hong Kong': 'HKG',
        'Chengdu': 'CTU',
        'Hangzhou': 'HGH',
        'Xi\'an': 'XIY',
        'Wuhan': 'WUH',
        'Chongqing': 'CKG',

        # Japanese Airports
        'Tokyo': 'NRT',
        'Tokyo Narita': 'NRT',
        'Tokyo Haneda': 'HND',
        'Osaka': 'KIX',
        'Osaka Kansai': 'KIX',
        'Kyoto': 'KIX',  # Kyoto uses Osaka airport
        'Nagoya': 'NGO',

        # Other Asian Airports
        'Seoul': 'ICN',
        'Singapore': 'SIN',
        'Bangkok': 'BKK',

        # European and American Airports
        'New York': 'JFK',
        'London': 'LHR',
        'Paris': 'CDG',
        'Los Angeles': 'LAX',
        'San Francisco': 'SFO',
    }

    @classmethod
    def get_deepseek_client(cls):
        """Get DeepSeek client"""
        return OpenAI(
            api_key=cls.DEEPSEEK_API_KEY,
            base_url=cls.DEEPSEEK_BASE_URL
        )

    @classmethod
    def get_city_coordinates(cls, city: str) -> tuple:
        """Get city coordinates"""
        return cls.CITY_COORDINATES.get(city, (39.9042, 116.4074))  # Default to Beijing

    @classmethod
    def get_airport_code(cls, city: str) -> str:
        """Get airport code"""
        return cls.AIRPORT_CODES.get(city, 'PEK')  # Default to Beijing Capital Airport