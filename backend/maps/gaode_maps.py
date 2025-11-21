# import requests
# from config.config import Config
# """   
#    - 路线规划（驾车、公交、步行）
#    - 计算两地距离和时间
#    - 地点搜索（POI搜索）
#    - 获取地点详情和坐标
# """

# class GaodeMapAPI:
#     def __init__(self):
#         self.api_key = Config.GAODE_API_KEY
#         self.base_url = "https://restapi.amap.com/v3"
#         self.session = requests.Session()

#     # -------------------- 通用内部方法 --------------------
#     def _get(self, url, params):
#         """统一 GET 封装：带异常处理、状态码检查、返回 JSON"""
#         try:
#             resp = self.session.get(url, params=params, timeout=5)
#             resp.raise_for_status()
#             data = resp.json()
#             if data.get("status") != "1":
#                 raise ValueError(f"高德接口错误: {data.get('info')}")
#             return data
#         except requests.RequestException as e:
#             raise RuntimeError(f"网络请求失败: {e}")

#     # -------------------- 地点搜索 --------------------
#     def search_place(self, city, keyword, page=1, offset=20):
#         """关键词搜索 POI"""
#         url = f"{self.base_url}/place/text"
#         params = {"key": self.api_key, "keywords": keyword,
#                   "city": city, "citylimit": True,
#                   "page": page, "offset": offset}
#         return self._get(url, params)

#     # -------------------- 路线规划 --------------------
#     def plan_route(self, origin: str, destination: str, mode="driving"):
#         """
#         规划路线
#         mode: driving | walking | transit
#         origin/destination: "lon,lat"
#         """
#         url = f"{self.base_url}/direction/{mode}"
#         params = {"key": self.api_key, "origin": origin, "destination": destination}
#         data = self._get(url, params)
#         # 提取最常用字段，简化前端使用
#         if mode == "transit":
#             route = data["route"]["transits"][0]  # 第一条公交方案
#             duration = int(route["duration"])  # 秒
#             distance = int(route["distance"])  # 米
#         else:
#             path = data["route"]["paths"][0]
#             duration = int(path["duration"])
#             distance = int(path["distance"])
#         return {"distance": distance, "duration": duration, "raw": data}

#     # -------------------- 距离矩阵 --------------------
#     def calculate_distance(self, origins, destination, mode="driving", batch=False):
#         """
#         mode 可选 driving | walking | bicycling
#         当 mode 存在时返回**实际导航距离**，否则保持原来直线距离
#         """
#         if mode:  # 想要真实路程
#             origins_list = origins.split('|')
#             results = []
#             for loc in origins_list:
#                 route_data = self.plan_route(loc, destination, mode)
#                 results.append(route_data["distance"])
#             return results if batch else results[0]

#         # 下面仍是原来直线距离逻辑，保持不变
#         url = f"{self.base_url}/distance"
#         params = {"key": self.api_key, "origins": origins,
#                   "destination": destination, "type": 1}
#         data = self._get(url, params)
#         results = [int(i["distance"]) for i in data["results"]]
#         return results if batch else results[0]

#     # -------------------- 逆地理编码 --------------------
#     def regeo(self, location: str, poitype=None, radius=1000):
#         """坐标→地址"""
#         url = f"{self.base_url}/geocode/regeo"
#         params = {"key": self.api_key, "location": location,
#                   "poitype": poitype, "radius": radius}
#         return self._get(url, params)

#     # -------------------- 地理编码 --------------------
#     def geo(self, address: str, city=None):
#         """地址→坐标"""
#         url = f"{self.base_url}/geocode/geo"
#         params = {"key": self.api_key, "address": address}
#         if city:
#             params["city"] = city
#         return self._get(url, params)



import requests
from config.config import Config
"""   
   - Route Planning (Driving, Transit, Walking)
   - Calculate Distance and Time between locations
   - Place Search (POI Search)
   - Get Location Details and Coordinates
"""

class GaodeMapAPI:
    def __init__(self):
        self.api_key = Config.GAODE_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
        self.session = requests.Session()

    # -------------------- General Internal Methods --------------------
    def _get(self, url, params):
        """Unified GET wrapper: includes exception handling, status code check, returns JSON"""
        try:
            resp = self.session.get(url, params=params, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            if data.get("status") != "1":
                raise ValueError(f"Gaode Interface Error: {data.get('info')}")
            return data
        except requests.RequestException as e:
            raise RuntimeError(f"Network Request Failed: {e}")

    # -------------------- Place Search --------------------
    def search_place(self, city, keyword, page=1, offset=20):
        """Keyword POI Search"""
        url = f"{self.base_url}/place/text"
        params = {"key": self.api_key, "keywords": keyword,
                  "city": city, "citylimit": True,
                  "page": page, "offset": offset}
        return self._get(url, params)

    # -------------------- Route Planning --------------------
    def plan_route(self, origin: str, destination: str, mode="driving"):
        """
        Plan Route
        mode: driving | walking | transit
        origin/destination: "lon,lat"
        """
        url = f"{self.base_url}/direction/{mode}"
        params = {"key": self.api_key, "origin": origin, "destination": destination}
        data = self._get(url, params)
        # Extract most commonly used fields, simplify frontend usage
        if mode == "transit":
            route = data["route"]["transits"][0]  # First transit option
            duration = int(route["duration"])  # seconds
            distance = int(route["distance"])  # meters
        else:
            path = data["route"]["paths"][0]
            duration = int(path["duration"])
            distance = int(path["distance"])
        return {"distance": distance, "duration": duration, "raw": data}

    # -------------------- Distance Matrix --------------------
    def calculate_distance(self, origins, destination, mode="driving", batch=False):
        """
        mode options: driving | walking | bicycling
        If mode exists, returns **actual navigation distance**, otherwise keeps original straight-line distance
        """
        if mode:  # Want actual route distance
            origins_list = origins.split('|')
            results = []
            for loc in origins_list:
                route_data = self.plan_route(loc, destination, mode)
                results.append(route_data["distance"])
            return results if batch else results[0]

        # Below is still the original straight-line distance logic, kept unchanged
        url = f"{self.base_url}/distance"
        params = {"key": self.api_key, "origins": origins,
                  "destination": destination, "type": 1}
        data = self._get(url, params)
        results = [int(i["distance"]) for i in data["results"]]
        return results if batch else results[0]

    # -------------------- Reverse Geocoding --------------------
    def regeo(self, location: str, poitype=None, radius=1000):
        """Coordinates -> Address"""
        url = f"{self.base_url}/geocode/regeo"
        params = {"key": self.api_key, "location": location,
                  "poitype": poitype, "radius": radius}
        return self._get(url, params)

    # -------------------- Geocoding --------------------
    def geo(self, address: str, city=None):
        """Address -> Coordinates"""
        url = f"{self.base_url}/geocode/geo"
        params = {"key": self.api_key, "address": address}
        if city:
            params["city"] = city
        return self._get(url, params)