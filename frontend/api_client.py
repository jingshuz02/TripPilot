
import requests
import streamlit as st
import ast
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from database.models import FlightOffer, FlightAmenity, Hotel, HotelOffer, HotelSentiment

class APIClient:
    def __init__(self, base_url="http://localhost:5000", db_url="sqlite:///../database/db.sql"):
        """
        初始化客户端
        :param base_url: 后端 API 地址
        :param db_url: 数据库连接地址，直接连接 db.sql 二进制文件
        """
        self.base_url = base_url
        # check_same_thread=False 用于 Streamlit 这种多线程环境
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        self.Session = sessionmaker(bind=self.engine)

    def _get_session(self):
        """获取一个新的数据库会话"""
        return self.Session()

    def _safe_parse(self, data_str):
        """
        辅助工具：安全地解析存储为字符串的 JSON 或 Python 字典数据
        例如: "{'weight': 23}" -> {'weight': 23}
        """
        if not data_str:
            return None
        try:
            # 尝试解析 Python 风格的字符串字典
            return ast.literal_eval(data_str)
        except:
            try:
                # 尝试解析标准 JSON
                return json.loads(data_str)
            except:
                # 解析失败，返回原始字符串
                return data_str

    # =======================
    #  Core API Methods
    # =======================

    def check_health(self):
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=2)
            return resp.status_code == 200
        except:
            return False
        

    def chat(self, prompt, preferences):
        """
        发送用户需求和旅行偏好给后端
        prompt: 用户输入的文本需求
        preferences: 侧边栏的旅行偏好（预算、日期等）
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "prompt": prompt,
                    "preferences": preferences  # 包含预算、出发/返回日期、语言等
                },
                timeout=30
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"发送需求失败: {str(e)}")
            return None

    def search_flights(self, origin, destination, date, adults=1, travel_class="ECONOMY"):
        """调用后端搜索航班，并返回航班ID列表"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "origin": origin, "destination": destination,
                    "date": date, "adults": adults, "travel_class": travel_class
                }, timeout=20
            )
            if response.status_code == 200:
                return response.json().get("flight_ids", [])
            st.error(f"航班搜索错误: {response.text}")
            return []
        except Exception as e:
            st.error(f"连接后端失败: {e}")
            return []

    def search_hotels(self, city, check_in, check_out, budget=None):
        """调用后端搜索酒店"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "city": city, "check_in": check_in,
                    "check_out": check_out, "budget": budget
                }, timeout=20
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"酒店搜索失败: {e}")
            return None

    def search_schedule(self, destination, start_date, end_date, interests=None, budget=None):
        """调用后端生成行程"""
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "destination": destination, "start_date": start_date,
                    "end_date": end_date, "interests": interests or [], "budget": budget
                }, timeout=30
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"行程生成失败: {e}")
            return None

    # =======================
    #  Database Retrieval Methods
    # =======================

    def get_flight_details(self, flight_id):
        """
        从数据库获取完整的航班信息，包括关联的设施 (Amenities)
        """
        session = self._get_session()
        try:
            # 1. 查询 FlightOffer，并预加载 (joinedload) 关联的 amenities
            # 这样可以避免多次查询数据库，提升效率
            flight = session.query(FlightOffer)\
                .options(joinedload(FlightOffer.amenities))\
                .filter(FlightOffer.id == str(flight_id))\
                .first()

            if not flight:
                return None

            # 2. 处理设施列表 (Relationship)
            amenities_list = []
            for amenity in flight.amenities:
                amenities_list.append({
                    "description": amenity.description,
                    "is_chargeable": amenity.is_chargeable,
                    "type": amenity.amenity_type,
                    "provider": amenity.amenity_provider
                })

            # 3. 组装返回给前端的完整字典
            return {
                "id": flight.id,
                "source": flight.source,
                "airline": {
                    "code": flight.carrier_code,
                    "name": flight.operating_carrier,
                    "flight_number": flight.flight_number,
                    "aircraft": flight.aircraft_code
                },
                "itinerary": {
                    "departure": {
                        "iata": flight.departure_iata,
                        "time": flight.departure_time
                    },
                    "arrival": {
                        "iata": flight.arrival_iata,
                        "time": flight.arrival_time
                    },
                    "duration": flight.duration
                },
                "price": {
                    "total": flight.total_price,
                    "base": flight.base_price,
                    "currency": flight.currency,
                    "grand_total": flight.grand_total
                },
                "cabin": {
                    "class": flight.cabin_class,
                    "branded_fare": flight.branded_fare
                },
                "bags": {
                    "checked": self._safe_parse(flight.included_checked_bags),
                    "cabin": self._safe_parse(flight.included_cabin_bags)
                },
                "amenities": amenities_list,  # 这里包含了关联表的数据
                "seats_available": flight.number_of_bookable_seats,
                "last_ticketing_date": flight.last_ticketing_date
            }
        except Exception as e:
            st.error(f"读取航班详情失败 (ID: {flight_id}): {str(e)}")
            return None
        finally:
            session.close()

    def get_hotel_details(self, hotel_id):
        """
        从数据库获取完整的酒店信息
        包含：酒店基本信息 + 关联的报价(Offers) + 关联的评价(Sentiments)
        """
        session = self._get_session()
        try:
            # 1. 查询 Hotel 基础信息
            hotel = session.query(Hotel).filter(Hotel.id == str(hotel_id)).first()
            
            if not hotel:
                return None

            # 2. 查询关联的 Offers (因为 Model 中没有定义 back_populates，我们需要手动查)
            # 或者如果在 Model 里加了 relationship，可以直接 hotel.offers
            offers = session.query(HotelOffer).filter(HotelOffer.hotel_id == str(hotel_id)).all()
            
            # 3. 查询关联的 Sentiments
            sentiment = session.query(HotelSentiment).filter(HotelSentiment.hotel_id == str(hotel_id)).first()

            # 4. 格式化 Offers 列表
            offers_data = []
            for off in offers:
                offers_data.append({
                    "offer_id": off.id,
                    "check_in": off.check_in_date,
                    "check_out": off.check_out_date,
                    "room": {
                        "type": off.room_type,
                        "description": off.room_description
                    },
                    "price": {
                        "total": off.total_price,
                        "currency": off.currency,
                        "base": off.base_price
                    },
                    "guests": {
                        "adults": off.adults,
                        "children": off.children
                    },
                    "policy": {
                        "refundable": off.refundable,
                        "payment": off.payment_type
                    }
                })

            # 5. 格式化 Sentiment (如果有)
            sentiment_data = {}
            if sentiment:
                sentiment_data = {
                    "overall_rating": sentiment.overall_rating,
                    "review_count": sentiment.number_of_reviews,
                    "details": {
                        "staff": sentiment.staff_rating,
                        "location": sentiment.location_rating,
                        "cleanliness": sentiment.room_comforts_rating, # 假设 mapping
                        "service": sentiment.service_rating,
                        "value": sentiment.value_for_money_rating
                    }
                }

            # 6. 组装最终酒店大字典
            return {
                "id": hotel.id,
                "name": hotel.name,
                "location": {
                    "city": hotel.city_name,
                    "country": hotel.country_code,
                    "coordinates": {"lat": hotel.latitude, "lon": hotel.longitude},
                    "address": self._safe_parse(hotel.address_lines),
                    "distance": f"{hotel.distance_value} {hotel.distance_unit}"
                },
                "rating": hotel.rating,
                "offers": offers_data,       # 包含所有报价
                "sentiment": sentiment_data  # 包含所有评价
            }

        except Exception as e:
            st.error(f"读取酒店详情失败 (ID: {hotel_id}): {str(e)}")
            return None
        finally:
            session.close()

      
    def get_weather(self, city, start_date, end_date):
        """获取天气接口"""
        try:
            response = requests.get(
                f"{self.base_url}/api/chat",  # 独立的天气接口
                params={
                    "city": city,
                    "start_date": start_date,
                    'end_date': end_date
                },
                timeout=5
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"获取天气失败: {str(e)}")
            return None
