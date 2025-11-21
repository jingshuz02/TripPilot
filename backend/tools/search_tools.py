# """
# 搜索工具 - 景点、餐厅搜索
# 注: 目前使用模拟数据，等待Serper API集成
# """
# import requests
# import sys
# import os

# # 添加项目根目录到路径
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# class SearchTool:
#     """搜索工具类 - 景点、餐厅搜索"""

#     def __init__(self, base_url="http://localhost:5000"):
#         """
#         初始化搜索工具

#         Args:
#             base_url: Flask后端地址
#         """
#         self.base_url = base_url

#         # 模拟数据库 - 等待Junjie实现Serper API后替换
#         self.mock_attractions = {
#             "东京": [
#                 {
#                     "name": "浅草寺",
#                     "description": "东京最古老的寺庙，以雷门和仲见世商店街闻名",
#                     "rating": 4.5,
#                     "type": "历史文化",
#                     "hours": "6:00-17:00",
#                     "price": "免费"
#                 },
#                 {
#                     "name": "东京塔",
#                     "description": "东京的地标建筑，可俯瞰城市全景",
#                     "rating": 4.3,
#                     "type": "观光景点",
#                     "hours": "9:00-23:00",
#                     "price": "¥1200起"
#                 },
#                 {
#                     "name": "明治神宫",
#                     "description": "供奉明治天皇的神社，被原始森林环绕",
#                     "rating": 4.6,
#                     "type": "历史文化",
#                     "hours": "日出-日落",
#                     "price": "免费"
#                 },
#                 {
#                     "name": "涩谷十字路口",
#                     "description": "世界最繁忙的十字路口之一，东京的象征",
#                     "rating": 4.4,
#                     "type": "城市景观",
#                     "hours": "全天",
#                     "price": "免费"
#                 },
#                 {
#                     "name": "富士山五合目",
#                     "description": "富士山半山腰观景点，可近距离欣赏富士山",
#                     "rating": 4.7,
#                     "type": "自然景观",
#                     "hours": "8:00-17:00（季节性）",
#                     "price": "免费（交通费另计）"
#                 }
#             ],
#             "北京": [
#                 {
#                     "name": "故宫",
#                     "description": "中国明清两代的皇家宫殿，世界文化遗产",
#                     "rating": 4.8,
#                     "type": "历史文化",
#                     "hours": "8:30-17:00",
#                     "price": "¥60"
#                 },
#                 {
#                     "name": "长城（八达岭）",
#                     "description": "世界七大奇迹之一，中国的象征",
#                     "rating": 4.7,
#                     "type": "历史文化",
#                     "hours": "7:30-18:00",
#                     "price": "¥40"
#                 },
#                 {
#                     "name": "天坛",
#                     "description": "明清皇帝祭天的场所，建筑精美",
#                     "rating": 4.6,
#                     "type": "历史文化",
#                     "hours": "6:00-22:00",
#                     "price": "¥15"
#                 }
#             ],
#             "上海": [
#                 {
#                     "name": "外滩",
#                     "description": "上海的象征，可欣赏黄浦江两岸美景",
#                     "rating": 4.7,
#                     "type": "城市景观",
#                     "hours": "全天",
#                     "price": "免费"
#                 },
#                 {
#                     "name": "东方明珠塔",
#                     "description": "上海地标建筑，可360度俯瞰城市",
#                     "rating": 4.4,
#                     "type": "观光景点",
#                     "hours": "8:00-22:00",
#                     "price": "¥180起"
#                 }
#             ]
#         }

#         self.mock_restaurants = {
#             "东京": [
#                 {
#                     "name": "数寄屋桥次郎",
#                     "cuisine": "寿司",
#                     "rating": 4.8,
#                     "price_range": "¥¥¥¥",
#                     "description": "米其林三星寿司店，需提前预约"
#                 },
#                 {
#                     "name": "一兰拉面",
#                     "cuisine": "拉面",
#                     "rating": 4.5,
#                     "price_range": "¥",
#                     "description": "著名豚骨拉面连锁店，24小时营业"
#                 },
#                 {
#                     "name": "鸟贵族",
#                     "cuisine": "居酒屋",
#                     "rating": 4.3,
#                     "price_range": "¥¥",
#                     "description": "平价居酒屋，串烧美味"
#                 }
#             ],
#             "北京": [
#                 {
#                     "name": "全聚德",
#                     "cuisine": "北京烤鸭",
#                     "rating": 4.5,
#                     "price_range": "¥¥¥",
#                     "description": "百年老字号，北京烤鸭代表"
#                 },
#                 {
#                     "name": "庆丰包子铺",
#                     "cuisine": "包子",
#                     "rating": 4.2,
#                     "price_range": "¥",
#                     "description": "传统北京小吃，物美价廉"
#                 }
#             ],
#             "上海": [
#                 {
#                     "name": "小笼包",
#                     "cuisine": "上海菜",
#                     "rating": 4.6,
#                     "price_range": "¥¥",
#                     "description": "正宗上海小笼包，汤汁鲜美"
#                 }
#             ]
#         }

#     def search_attractions(self, city: str) -> list:
#         """
#         搜索景点

#         Args:
#             city: 城市名称

#         Returns:
#             景点列表
#         """
#         # TODO: 等待Junjie实现Serper API后，替换为真实搜索
#         # 目前返回模拟数据

#         attractions = []

#         # 尝试从模拟数据中查找
#         for key in self.mock_attractions.keys():
#             if key in city or city in key:
#                 attractions = self.mock_attractions[key]
#                 break

#         # 如果没找到，返回默认数据
#         if not attractions:
#             attractions = [
#                 {
#                     "name": f"{city}景点1",
#                     "description": f"这是{city}的一个著名景点",
#                     "rating": 4.5,
#                     "type": "观光景点",
#                     "hours": "9:00-18:00",
#                     "price": "待查询"
#                 }
#             ]

#         # 添加ID
#         for i, attr in enumerate(attractions):
#             attr['id'] = f"attr_{i}"

#         return attractions

#     def search_restaurants(self, city: str, cuisine: str = None) -> list:
#         """
#         搜索餐厅

#         Args:
#             city: 城市名称
#             cuisine: 菜系（可选）

#         Returns:
#             餐厅列表
#         """
#         # TODO: 等待Junjie实现Serper API后，替换为真实搜索
#         # 目前返回模拟数据

#         restaurants = []

#         # 尝试从模拟数据中查找
#         for key in self.mock_restaurants.keys():
#             if key in city or city in key:
#                 restaurants = self.mock_restaurants[key]
#                 break

#         # 如果指定了菜系，筛选
#         if cuisine and restaurants:
#             restaurants = [r for r in restaurants if cuisine.lower() in r['cuisine'].lower()]

#         # 如果没找到，返回默认数据
#         if not restaurants:
#             restaurants = [
#                 {
#                     "name": f"{city}餐厅1",
#                     "cuisine": "本地美食",
#                     "rating": 4.0,
#                     "price_range": "¥¥",
#                     "description": f"{city}的特色餐厅"
#                 }
#             ]

#         # 添加ID
#         for i, rest in enumerate(restaurants):
#             rest['id'] = f"rest_{i}"

#         return restaurants

#     def search_general(self, query: str) -> dict:
#         """
#         通用搜索（等待Serper API实现）

#         Args:
#             query: 搜索查询

#         Returns:
#             搜索结果
#         """
#         # TODO: 调用Serper API
#         return {
#             'query': query,
#             'results': [],
#             'message': '通用搜索功能正在开发中，请等待Serper API集成'
#         }


# # 测试代码
# if __name__ == "__main__":
#     tool = SearchTool()

#     print("=" * 50)
#     print("测试搜索工具")
#     print("=" * 50)

#     # 测试景点搜索
#     print("\n1. 搜索东京景点:")
#     attractions = tool.search_attractions("东京")
#     for attr in attractions:
#         print(f"  📍 {attr['name']}: {attr['description'][:30]}...")

#     # 测试餐厅搜索
#     print("\n2. 搜索东京餐厅:")
#     restaurants = tool.search_restaurants("东京")
#     for rest in restaurants:
#         print(f"  🍽️  {rest['name']}: {rest['cuisine']} - {rest['price_range']}")




"""
Search Tools - Attraction and Restaurant Search
Note: Currently uses mock data, awaiting Serper API integration.
"""
import requests
import sys
import os

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class SearchTool:
    """Search Tool Class - Attraction and Restaurant Search"""

    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize Search Tool

        Args:
            base_url: Flask backend address
        """
        self.base_url = base_url

        # Mock Database - To be replaced after Junjie implements Serper API
        self.mock_attractions = {
            "Tokyo": [
                {
                    "name": "Senso-ji Temple",
                    "description": "Tokyo's oldest temple, famous for Kaminarimon (Thunder Gate) and Nakamise-dori street",
                    "rating": 4.5,
                    "type": "History & Culture",
                    "hours": "6:00-17:00",
                    "price": "Free"
                },
                {
                    "name": "Tokyo Tower",
                    "description": "A landmark of Tokyo, offering panoramic city views",
                    "rating": 4.3,
                    "type": "Observation Deck",
                    "hours": "9:00-23:00",
                    "price": "¥1200 onwards"
                },
                {
                    "name": "Meiji Jingu",
                    "description": "A shrine dedicated to Emperor Meiji, surrounded by a forest",
                    "rating": 4.6,
                    "type": "History & Culture",
                    "hours": "Sunrise to Sunset",
                    "price": "Free"
                },
                {
                    "name": "Shibuya Crossing",
                    "description": "One of the world's busiest intersections, a symbol of Tokyo",
                    "rating": 4.4,
                    "type": "Cityscape",
                    "hours": "All Day",
                    "price": "Free"
                },
                {
                    "name": "Mount Fuji 5th Station",
                    "description": "An observation point halfway up Mt. Fuji, offering close-up views",
                    "rating": 4.7,
                    "type": "Natural Scenery",
                    "hours": "8:00-17:00 (Seasonal)",
                    "price": "Free (Transportation cost separate)"
                }
            ],
            "Beijing": [
                {
                    "name": "The Forbidden City",
                    "description": "The imperial palace of the Ming and Qing dynasties, a UNESCO World Heritage site",
                    "rating": 4.8,
                    "type": "History & Culture",
                    "hours": "8:30-17:00",
                    "price": "¥60"
                },
                {
                    "name": "Great Wall (Badaling)",
                    "description": "One of the Seven Wonders of the World, a symbol of China",
                    "rating": 4.7,
                    "type": "History & Culture",
                    "hours": "7:30-18:00",
                    "price": "¥40"
                },
                {
                    "name": "Temple of Heaven",
                    "description": "The site where emperors performed Heaven worship rituals, featuring exquisite architecture",
                    "rating": 4.6,
                    "type": "History & Culture",
                    "hours": "6:00-22:00",
                    "price": "¥15"
                }
            ],
            "Shanghai": [
                {
                    "name": "The Bund",
                    "description": "The symbol of Shanghai, offering scenic views of the Huangpu River banks",
                    "rating": 4.7,
                    "type": "Cityscape",
                    "hours": "All Day",
                    "price": "Free"
                },
                {
                    "name": "Oriental Pearl Tower",
                    "description": "A Shanghai landmark, offering 360-degree city views",
                    "rating": 4.4,
                    "type": "Observation Deck",
                    "hours": "8:00-22:00",
                    "price": "¥180 onwards"
                }
            ]
        }

        self.mock_restaurants = {
            "Tokyo": [
                {
                    "name": "Sukiyabashi Jiro",
                    "cuisine": "Sushi",
                    "rating": 4.8,
                    "price_range": "¥¥¥¥",
                    "description": "Three-Michelin-star sushi restaurant, reservation required"
                },
                {
                    "name": "Ichiran Ramen",
                    "cuisine": "Ramen",
                    "rating": 4.5,
                    "price_range": "¥",
                    "description": "Famous tonkotsu ramen chain, open 24 hours"
                },
                {
                    "name": "Torikizoku",
                    "cuisine": "Izakaya",
                    "rating": 4.3,
                    "price_range": "¥¥",
                    "description": "Affordable izakaya, delicious yakitori (skewers)"
                }
            ],
            "Beijing": [
                {
                    "name": "Quanjude",
                    "cuisine": "Peking Duck",
                    "rating": 4.5,
                    "price_range": "¥¥¥",
                    "description": "Centuries-old brand, representative of Peking Duck"
                },
                {
                    "name": "Qingfeng Steamed Buns",
                    "cuisine": "Baozi (Buns)",
                    "rating": 4.2,
                    "price_range": "¥",
                    "description": "Traditional Beijing snack, good value for money"
                }
            ],
            "Shanghai": [
                {
                    "name": "Xiaolongbao (Soup Dumplings)",
                    "cuisine": "Shanghai Cuisine",
                    "rating": 4.6,
                    "price_range": "¥¥",
                    "description": "Authentic Shanghai soup dumplings, flavorful broth"
                }
            ]
        }

    def search_attractions(self, city: str) -> list:
        """
        Search for attractions

        Args:
            city: City Name

        Returns:
            List of attractions
        """
        # TODO: Await implementation of Serper API by Junjie, then replace with real search
        # Currently returns mock data

        attractions = []

        # Attempt to find in mock data
        for key in self.mock_attractions.keys():
            if key in city or city in key:
                attractions = self.mock_attractions[key]
                break

        # If not found, return default data
        if not attractions:
            attractions = [
                {
                    "name": f"{city} Attraction 1",
                    "description": f"A famous attraction in {city}",
                    "rating": 4.5,
                    "type": "Sightseeing Spot",
                    "hours": "9:00-18:00",
                    "price": "To be queried"
                }
            ]

        # Add ID
        for i, attr in enumerate(attractions):
            attr['id'] = f"attr_{i}"

        return attractions

    def search_restaurants(self, city: str, cuisine: str = None) -> list:
        """
        Search for restaurants

        Args:
            city: City Name
            cuisine: Cuisine type (Optional)

        Returns:
            List of restaurants
        """
        # TODO: Await implementation of Serper API by Junjie, then replace with real search
        # Currently returns mock data

        restaurants = []

        # Attempt to find in mock data
        for key in self.mock_restaurants.keys():
            if key in city or city in key:
                restaurants = self.mock_restaurants[key]
                break

        # If cuisine is specified, filter
        if cuisine and restaurants:
            restaurants = [r for r in restaurants if cuisine.lower() in r['cuisine'].lower()]

        # If not found, return default data
        if not restaurants:
            restaurants = [
                {
                    "name": f"{city} Restaurant 1",
                    "cuisine": "Local Delicacies",
                    "rating": 4.0,
                    "price_range": "¥¥",
                    "description": f"A featured restaurant in {city}"
                }
            ]

        # Add ID
        for i, rest in enumerate(restaurants):
            rest['id'] = f"rest_{i}"

        return restaurants

    def search_general(self, query: str) -> dict:
        """
        General Search (Awaiting Serper API implementation)

        Args:
            query: Search query

        Returns:
            Search results
        """
        # TODO: Call Serper API
        return {
            'query': query,
            'results': [],
            'message': 'General search function is currently under development, awaiting Serper API integration'
        }


# Testing code
if __name__ == "__main__":
    tool = SearchTool()

    print("=" * 50)
    print("Testing Search Tool")
    print("=" * 50)

    # Test attraction search
    print("\n1. Searching Tokyo Attractions:")
    attractions = tool.search_attractions("Tokyo")
    for attr in attractions:
        print(f"  📍 {attr['name']}: {attr['description'][:30]}...")

    # Test restaurant search
    print("\n2. Searching Tokyo Restaurants:")
    restaurants = tool.search_restaurants("Tokyo")
    for rest in restaurants:
        print(f"  🍽️  {rest['name']}: {rest['cuisine']} - {rest['price_range']}")