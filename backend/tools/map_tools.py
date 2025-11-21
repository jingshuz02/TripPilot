# """
# 地图工具 - 封装高德地图API
# """
# import requests
# import sys
# import os

# # 添加项目根目录到路径
# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# class MapTool:
#     """地图工具类 - 地点搜索、路线规划"""

#     def __init__(self, base_url="http://localhost:5000"):
#         """
#         初始化地图工具

#         Args:
#             base_url: Flask后端地址
#         """
#         self.base_url = base_url

#     def search_place(self, city: str, keyword: str) -> dict:
#         """
#         搜索地点

#         Args:
#             city: 城市名称
#             keyword: 搜索关键词（如"浅草寺"、"东京塔"）

#         Returns:
#             {
#                 'success': True/False,
#                 'places': [
#                     {
#                         'name': '地点名称',
#                         'address': '详细地址',
#                         'location': '经度,纬度',
#                         'type': '类型'
#                     }
#                 ]
#             }
#         """
#         try:
#             response = requests.get(
#                 f"{self.base_url}/api/map/search",
#                 params={
#                     "city": city,
#                     "keyword": keyword
#                 },
#                 timeout=5
#             )

#             if response.status_code == 200:
#                 data = response.json()

#                 if data.get("code") == 0:
#                     places_data = data.get("data", {})
#                     pois = places_data.get("pois", [])

#                     places = []
#                     for poi in pois:
#                         places.append({
#                             'name': poi.get('name', 'N/A'),
#                             'address': poi.get('address', 'N/A'),
#                             'location': poi.get('location', 'N/A'),
#                             'type': poi.get('type', 'N/A'),
#                             'tel': poi.get('tel', 'N/A')
#                         })

#                     return {
#                         'success': True,
#                         'places': places,
#                         'count': len(places)
#                     }
#                 else:
#                     return {
#                         'success': False,
#                         'error': data.get('msg', 'Unknown error'),
#                         'places': []
#                     }
#             else:
#                 return {
#                     'success': False,
#                     'error': f'HTTP {response.status_code}',
#                     'places': []
#                 }

#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e),
#                 'places': []
#             }

#     def plan_route(self, origin: str, destination: str, mode: str = "driving") -> dict:
#         """
#         规划路线

#         Args:
#             origin: 起点（可以是地名或"经度,纬度"）
#             destination: 终点
#             mode: 出行方式 ("driving" 驾车 或 "walking" 步行)

#         Returns:
#             {
#                 'success': True/False,
#                 'distance': '距离（米）',
#                 'duration': '时间（秒）',
#                 'route': '路线描述',
#                 'steps': [...]  # 详细步骤
#             }
#         """
#         try:
#             # 如果输入的不是坐标，先搜索获取坐标
#             if ',' not in origin:
#                 # 搜索起点坐标
#                 place_result = self.search_place("", origin)
#                 if place_result['success'] and place_result['places']:
#                     origin = place_result['places'][0]['location']
#                 else:
#                     return {
#                         'success': False,
#                         'error': f'无法找到起点: {origin}'
#                     }

#             if ',' not in destination:
#                 # 搜索终点坐标
#                 place_result = self.search_place("", destination)
#                 if place_result['success'] and place_result['places']:
#                     destination = place_result['places'][0]['location']
#                 else:
#                     return {
#                         'success': False,
#                         'error': f'无法找到终点: {destination}'
#                     }

#             # 规划路线
#             response = requests.get(
#                 f"{self.base_url}/api/map/route",
#                 params={
#                     "origin": origin,
#                     "destination": destination,
#                     "mode": mode
#                 },
#                 timeout=10
#             )

#             if response.status_code == 200:
#                 data = response.json()

#                 if data.get("code") == 0:
#                     route_data = data.get("data", {})
#                     route = route_data.get("route", {})

#                     # 提取路线信息
#                     paths = route.get("paths", [{}])[0] if route.get("paths") else {}

#                     return {
#                         'success': True,
#                         'distance': paths.get('distance', 'N/A'),
#                         'duration': paths.get('duration', 'N/A'),
#                         'steps': paths.get('steps', []),
#                         'origin': origin,
#                         'destination': destination,
#                         'mode': mode
#                     }
#                 else:
#                     return {
#                         'success': False,
#                         'error': data.get('msg', 'Unknown error')
#                     }
#             else:
#                 return {
#                     'success': False,
#                     'error': f'HTTP {response.status_code}'
#                 }

#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e)
#             }

#     def calculate_distance(self, origins: str, destination: str, mode: str = None) -> dict:
#         """
#         计算距离

#         Args:
#             origins: 起点坐标，多个用|分隔
#             destination: 终点坐标
#             mode: 如果提供，计算路径距离；否则计算直线距离

#         Returns:
#             距离信息
#         """
#         try:
#             params = {
#                 "origins": origins,
#                 "destination": destination,
#                 "batch": "1"
#             }

#             if mode:
#                 params["mode"] = mode

#             response = requests.get(
#                 f"{self.base_url}/api/map/distance",
#                 params=params,
#                 timeout=5
#             )

#             if response.status_code == 200:
#                 data = response.json()

#                 if data.get("code") == 0:
#                     distance_data = data.get("data", {})

#                     return {
#                         'success': True,
#                         'results': distance_data.get("results", [])
#                     }
#                 else:
#                     return {
#                         'success': False,
#                         'error': data.get('msg', 'Unknown error')
#                     }
#             else:
#                 return {
#                     'success': False,
#                     'error': f'HTTP {response.status_code}'
#                 }

#         except Exception as e:
#             return {
#                 'success': False,
#                 'error': str(e)
#             }

#     def get_route_summary(self, origin: str, destination: str, mode: str = "driving") -> str:
#         """
#         获取路线摘要（文本格式）

#         Args:
#             origin: 起点
#             destination: 终点
#             mode: 出行方式

#         Returns:
#             路线摘要文本
#         """
#         result = self.plan_route(origin, destination, mode)

#         if not result['success']:
#             return f"无法规划路线: {result.get('error', '未知错误')}"

#         # 转换距离和时间
#         distance_km = float(result['distance']) / 1000 if result['distance'] != 'N/A' else 0
#         duration_min = int(result['duration']) / 60 if result['duration'] != 'N/A' else 0

#         mode_text = {"driving": "驾车", "walking": "步行"}.get(mode, mode)

#         summary = f"🚗 {mode_text}路线规划\n"
#         summary += f"📍 起点: {origin}\n"
#         summary += f"📍 终点: {destination}\n"
#         summary += f"📏 距离: {distance_km:.1f} 公里\n"
#         summary += f"⏱️  预计时间: {int(duration_min)} 分钟\n"

#         return summary


# # 测试代码
# if __name__ == "__main__":
#     tool = MapTool()

#     print("=" * 50)
#     print("测试地图工具")
#     print("=" * 50)

#     # 测试地点搜索
#     print("\n1. 搜索北京大学:")
#     result = tool.search_place("北京", "北京大学")
#     if result['success']:
#         print(f"找到 {result['count']} 个结果")
#         for place in result['places'][:3]:
#             print(f"  - {place['name']}: {place['address']}")

#     # 测试路线规划
#     print("\n2. 规划路线:")
#     print(tool.get_route_summary("116.481,39.990", "116.434,39.908", "driving"))








"""
Map Tools - Encapsulating Amap API
"""
import requests
import sys
import os

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class MapTool:
    """Map Tool Class - Place Search, Route Planning"""

    def __init__(self, base_url="http://localhost:5000"):
        """
        Initialize map tool

        Args:
            base_url: Flask backend address
        """
        self.base_url = base_url

    def search_place(self, city: str, keyword: str) -> dict:
        """
        Search for places

        Args:
            city: City name
            keyword: Search keyword (e.g., "Senso-ji Temple", "Tokyo Tower")

        Returns:
            {
                'success': True/False,
                'places': [
                    {
                        'name': 'Place name',
                        'address': 'Detailed address',
                        'location': 'longitude,latitude',
                        'type': 'Type'
                    }
                ]
            }
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/map/search",
                params={
                    "city": city,
                    "keyword": keyword
                },
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("code") == 0:
                    places_data = data.get("data", {})
                    pois = places_data.get("pois", [])

                    places = []
                    for poi in pois:
                        places.append({
                            'name': poi.get('name', 'N/A'),
                            'address': poi.get('address', 'N/A'),
                            'location': poi.get('location', 'N/A'),
                            'type': poi.get('type', 'N/A'),
                            'tel': poi.get('tel', 'N/A')
                        })

                    return {
                        'success': True,
                        'places': places,
                        'count': len(places)
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('msg', 'Unknown error'),
                        'places': []
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}',
                    'places': []
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'places': []
            }

    def plan_route(self, origin: str, destination: str, mode: str = "driving") -> dict:
        """
        Plan route

        Args:
            origin: Starting point (can be a place name or "longitude,latitude")
            destination: Destination
            mode: Travel mode ("driving" or "walking")

        Returns:
            {
                'success': True/False,
                'distance': 'Distance (meters)',
                'duration': 'Time (seconds)',
                'route': 'Route description',
                'steps': [...]  # Detailed steps
            }
        """
        try:
            # If input is not coordinates, first search to get coordinates
            if ',' not in origin:
                # Search for origin coordinates
                place_result = self.search_place("", origin)
                if place_result['success'] and place_result['places']:
                    origin = place_result['places'][0]['location']
                else:
                    return {
                        'success': False,
                        'error': f'Cannot find origin: {origin}'
                    }

            if ',' not in destination:
                # Search for destination coordinates
                place_result = self.search_place("", destination)
                if place_result['success'] and place_result['places']:
                    destination = place_result['places'][0]['location']
                else:
                    return {
                        'success': False,
                        'error': f'Cannot find destination: {destination}'
                    }

            # Plan route
            response = requests.get(
                f"{self.base_url}/api/map/route",
                params={
                    "origin": origin,
                    "destination": destination,
                    "mode": mode
                },
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("code") == 0:
                    route_data = data.get("data", {})
                    route = route_data.get("route", {})

                    # Extract route information
                    paths = route.get("paths", [{}])[0] if route.get("paths") else {}

                    return {
                        'success': True,
                        'distance': paths.get('distance', 'N/A'),
                        'duration': paths.get('duration', 'N/A'),
                        'steps': paths.get('steps', []),
                        'origin': origin,
                        'destination': destination,
                        'mode': mode
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('msg', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def calculate_distance(self, origins: str, destination: str, mode: str = None) -> dict:
        """
        Calculate distance

        Args:
            origins: Origin coordinates, multiple separated by |
            destination: Destination coordinate
            mode: If provided, calculate route distance; otherwise calculate straight-line distance

        Returns:
            Distance information
        """
        try:
            params = {
                "origins": origins,
                "destination": destination,
                "batch": "1"
            }

            if mode:
                params["mode"] = mode

            response = requests.get(
                f"{self.base_url}/api/map/distance",
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("code") == 0:
                    distance_data = data.get("data", {})

                    return {
                        'success': True,
                        'results': distance_data.get("results", [])
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('msg', 'Unknown error')
                    }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_route_summary(self, origin: str, destination: str, mode: str = "driving") -> str:
        """
        Get route summary (text format)

        Args:
            origin: Starting point
            destination: Destination
            mode: Travel mode

        Returns:
            Route summary text
        """
        result = self.plan_route(origin, destination, mode)

        if not result['success']:
            return f"Cannot plan route: {result.get('error', 'Unknown error')}"

        # Convert distance and time
        distance_km = float(result['distance']) / 1000 if result['distance'] != 'N/A' else 0
        duration_min = int(result['duration']) / 60 if result['duration'] != 'N/A' else 0

        mode_text = {"driving": "driving", "walking": "walking"}.get(mode, mode)

        summary = f"🚗 {mode_text} route planning\n"
        summary += f"📍 Origin: {origin}\n"
        summary += f"📍 Destination: {destination}\n"
        summary += f"📏 Distance: {distance_km:.1f} km\n"
        summary += f"⏱️  Estimated time: {int(duration_min)} minutes\n"

        return summary


# Test code
if __name__ == "__main__":
    tool = MapTool()

    print("=" * 50)
    print("Testing map tool")
    print("=" * 50)

    # Test place search
    print("\n1. Search for Peking University:")
    result = tool.search_place("Beijing", "Peking University")
    if result['success']:
        print(f"Found {result['count']} results")
        for place in result['places'][:3]:
            print(f"  - {place['name']}: {place['address']}")

    # Test route planning
    print("\n2. Plan route:")
    print(tool.get_route_summary("116.481,39.990", "116.434,39.908", "driving"))