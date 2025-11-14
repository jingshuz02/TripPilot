      
import requests
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from database.models import FlightOffer  # 导入数据库模型

class APIClient:
    def __init__(self, base_url="http://localhost:5000", db_url="sqlite:///../database/flight_db.db"):
        self.base_url = base_url
        # 初始化数据库连接（复用会话，避免频繁创建/关闭）
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def _get_db_session(self):
        """获取数据库会话（内部工具方法）"""
        return self.Session()

    def check_health(self):
        """检查后端健康状态"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def chat(self, prompt, preferences):
        """发送用户需求和旅行偏好给后端"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "prompt": prompt,
                    "preferences": preferences
                },
                timeout=30
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"发送需求失败: {str(e)}")
            return None

    def search_hotels(self, city, check_in, check_out, budget=None):
        """搜索酒店接口"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "city": city,
                    "check_in": check_in,
                    "check_out": check_out,
                    "budget": budget  
                },
                timeout=10
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"酒店搜索失败: {str(e)}")
            return None

    def search_flights(self, origin, destination, date, adults=1, travel_class="ECONOMY"):
        """
        搜索航班：调用后端接口获取航班ID列表
        返回值：航班ID列表（如["1", "2", "3"]）
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",  # 独立的航班搜索接口
                json={
                    "origin": origin,
                    "destination": destination,
                    "date": date,
                    "adults": adults,
                    "travel_class": travel_class
                },
                timeout=15
            )
            if response.status_code == 200:
                return response.json().get("flight_ids", [])  # 仅返回ID列表
            st.warning(f"航班搜索返回非成功状态：{response.status_code}")
            return []
        except Exception as e:
            st.error(f"航班搜索失败: {str(e)}")
            return []

    def get_flight_details(self, flight_id):
        """
        通过ID查询航班详情（从数据库读取）
        返回值：格式化的航班详情字典，或None
        """
        session = self._get_db_session()
        try:
            flight = session.query(FlightOffer).get(flight_id)
            if not flight:
                st.warning(f"未找到ID为 {flight_id} 的航班")
                return None
            # 格式化返回前端需要的字段
            return {
                "id": flight.id,
                "departure": {
                    "iata": flight.departure_iata,
                    "time": flight.departure_time
                },
                "arrival": {
                    "iata": flight.arrival_iata,
                    "time": flight.arrival_time
                },
                "carrier": flight.carrier_code,
                "flight_number": flight.flight_number,
                "aircraft": flight.aircraft_code,
                "duration": flight.duration,
                "price": flight.total_price,
                "currency": flight.currency,
                "cabin_class": flight.cabin_class,
                "bags": {
                    "checked": flight.included_checked_bags,
                    "cabin": flight.included_cabin_bags
                },
                "last_ticketing_date": flight.last_ticketing_date,
                "available_seats": flight.number_of_bookable_seats
            }
        except Exception as e:
            st.error(f"查询航班详情失败: {str(e)}")
            return None
        finally:
            session.close()  # 确保关闭会话



    # def search_flights(self, origin, destination, departure_date, return_date=None, adults=1, travel_class="ECONOMY"):
    #     """
    #     搜索航班接口
    #     origin: 出发地IATA代码（如"PEK"）
    #     destination: 目的地IATA代码（如"SYD"）
    #     departure_date: 出发日期（格式"YYYY-MM-DD"）
    #     return_date: 返回日期（单程可不填，格式"YYYY-MM-DD"）
    #     adults: 成人数量
    #     travel_class: 舱位等级（ECONOMY/BUSINESS/FIRST）
    #     """
    #     try:
    #         response = requests.post(
    #             f"{self.base_url}/api/chat",
    #             json={
    #                 "origin": origin,
    #                 "destination": destination,
    #                 "departure_date": departure_date,
    #                 "return_date": return_date,
    #                 "adults": adults,
    #                 "travel_class": travel_class
    #             },
    #             timeout=15
    #         )
    #         return response.json() if response.status_code == 200 else None
    #     except Exception as e:
    #         st.error(f"航班搜索失败: {str(e)}")
    #         return None
    
    def design_schedule(self, destination, start_date, end_date, interests=None, budget=None):
        """
        设计旅行日程接口
        destination: 目的地城市
        start_date: 开始日期（格式"YYYY-MM-DD"）
        end_date: 结束日期（格式"YYYY-MM-DD"）
        interests: 兴趣偏好（如["历史", "美食", "购物"]）
        budget: 每日预算
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "destination": destination,
                    "start_date": start_date,
                    "end_date": end_date,
                    "interests": interests or [],  # 默认为空列表
                    "budget": budget
                },
                timeout=20
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"日程设计失败: {str(e)}")
            return None
    
    def get_weather(self, city, date):
        """
        获取天气接口
        city: 城市名称
        date: 日期（格式"YYYY-MM-DD"，可查未来7天）
        """
        try:
            response = requests.get(
                f"{self.base_url}/api/chat",
                params={
                    "city": city,
                    "date": date
                },
                timeout=5
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"获取天气失败: {str(e)}")
            return None
