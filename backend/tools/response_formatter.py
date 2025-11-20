"""
响应格式转换器
将后端数据转换为前端需要的统一格式

前端期望格式：
{
  "action": "search_flights/search_hotels/get_weather/suggestion",
  "content": "描述性文字",
  "data": 结构化数据 或 null
}

作者: 曾婧姝
"""
from typing import Dict, Any, List, Optional
from datetime import datetime


class ResponseFormatter:
    """响应格式转换器"""
    
    @staticmethod
    def format_flights(flights_data: Dict, query_context: str = "") -> Dict:
        """
        格式化航班数据
        
        Args:
            flights_data: amadeus返回的航班数据
            query_context: 查询上下文（如"飞往东京"）
        """
        if not flights_data.get('success') or not flights_data.get('data'):
            return {
                "action": "search_flights",
                "content": "抱歉，未找到符合条件的航班。",
                "data": []
            }
        
        flights = flights_data['data']
        count = len(flights)
        
        # 生成描述性文字
        content = f"为您找到以下 {count} 趟{query_context}航班。"
        if flights_data.get('ai_enhanced_count', 0) > 0:
            content += f" （其中 {flights_data['ai_enhanced_count']} 趟航班由AI补充了部分信息）"
        
        # 转换为前端格式
        formatted_flights = []
        for flight in flights:
            formatted_flight = {
                "id": flight.get('id', 'unknown'),
                "departure_iata": flight.get('departure', {}).get('iataCode'),
                "arrival_iata": flight.get('arrival', {}).get('iataCode'),
                "departure_time": flight.get('departure', {}).get('at'),
                "arrival_time": flight.get('arrival', {}).get('at'),
                "duration": ResponseFormatter._format_duration(flight.get('duration')),
                "carrier_code": flight.get('carrierCode'),
                "flight_number": str(flight.get('number', '')),
                "aircraft_code": flight.get('aircraft'),
                "operating_carrier": ResponseFormatter._get_airline_name(flight.get('carrierCode')),
                "cabin_class": flight.get('cabinClass', 'ECONOMY'),
                "currency": flight.get('price', {}).get('currency', 'USD'),
                "total_price": float(flight.get('price', {}).get('total', 0)),
                "base_price": float(flight.get('price', {}).get('base', 0)),
                "grand_total": float(flight.get('price', {}).get('grandTotal', 0)),
                "number_of_bookable_seats": 9,  # Amadeus测试环境通常不返回这个
                "last_ticketing_date": ResponseFormatter._get_ticketing_date(),
                "included_checked_bags": ResponseFormatter._format_baggage(
                    flight.get('includedCheckedBags'),
                    flight.get('cabinClass')
                ),
                "included_cabin_bags": "1件 (7KG)",  # 标准值
                "amenities": flight.get('amenities', ResponseFormatter._get_default_amenities(
                    flight.get('carrierCode'),
                    flight.get('cabinClass')
                ))
            }
            
            # 标记AI增强的数据
            if flight.get('_ai_enhanced'):
                formatted_flight['_ai_enhanced'] = True
                formatted_flight['_ai_fields'] = flight.get('_ai_fields', [])
            
            formatted_flights.append(formatted_flight)
        
        return {
            "action": "search_flights",
            "content": content,
            "data": formatted_flights
        }
    
    @staticmethod
    def format_hotels(hotels_data: Dict, query_context: str = "") -> Dict:
        """
        格式化酒店数据
        
        Args:
            hotels_data: amadeus返回的酒店数据
            query_context: 查询上下文（如"位于新宿"）
        """
        if not hotels_data.get('success') or not hotels_data.get('hotels'):
            return {
                "action": "search_hotels",
                "content": "抱歉，未找到符合条件的酒店。",
                "data": []
            }
        
        hotels = hotels_data['hotels']
        offers = hotels_data.get('offers', [])
        reviews = hotels_data.get('reviews', [])
        count = len(hotels)
        
        # 生成描述性文字
        content = f"为您找到以下 {count} 家{query_context}酒店。"
        if hotels_data.get('ai_enhanced'):
            content += " （部分数据由AI生成补充）"
        
        # 构建酒店详情字典
        hotel_details = {}
        for hotel in hotels:
            hotel_id = hotel.get('hotelId')
            hotel_details[hotel_id] = {
                "id": hotel_id,
                "name": hotel.get('name', '未知酒店'),
                "location": hotel.get('address', {}).get('cityName', ''),
                "rating": 0,  # 从评价中获取
                "desc": "",
                "price": 0,
                "nights": 0,
                "total_price": 0,
                "amenities": []
            }
        
        # 填充价格信息
        for offer in offers:
            hotel_id = offer.get('hotel', {}).get('hotelId')
            if hotel_id in hotel_details:
                offer_data = offer.get('offers', [{}])[0]
                price = float(offer_data.get('price', {}).get('total', 0))
                hotel_details[hotel_id]['price'] = price
                hotel_details[hotel_id]['desc'] = offer_data.get('room', {}).get('description', {}).get('text', '')
                
                # 标记AI生成
                if offer_data.get('_source') == 'ai_generated':
                    hotel_details[hotel_id]['_ai_enhanced'] = True
        
        # 填充评价信息
        for review in reviews:
            hotel_id = review.get('hotelId')
            if hotel_id in hotel_details:
                rating = review.get('overallRating', 0)
                hotel_details[hotel_id]['rating'] = round(rating / 20, 1)  # 转换为5分制
        
        # 转换为列表
        formatted_hotels = list(hotel_details.values())
        
        return {
            "action": "search_hotels",
            "content": content,
            "data": formatted_hotels
        }
    
    @staticmethod
    def format_weather(weather_data: Dict, city: str) -> Dict:
        """
        格式化天气数据
        
        Args:
            weather_data: 天气API返回的数据
            city: 城市名
        """
        if not weather_data or 'error' in weather_data:
            return {
                "action": "get_weather",
                "content": f"抱歉，无法获取{city}的天气信息。",
                "data": None
            }
        
        # 生成描述性文字
        temp = weather_data.get('temperature', 0)
        desc = weather_data.get('weather', '未知')
        content = f"{city}的天气{desc}，当前温度 {temp}°C。"
        
        # 格式化数据
        formatted_weather = {
            "city_name": city,
            "temperature": temp,
            "feels_like": weather_data.get('temperature', temp),
            "description": desc,
            "humidity": weather_data.get('humidity', 50),
            "wind_speed": weather_data.get('windspeed', 0),
            "icon": ResponseFormatter._get_weather_icon(desc)
        }
        
        return {
            "action": "get_weather",
            "content": content,
            "data": formatted_weather
        }
    
    @staticmethod
    def format_suggestion(suggestion_text: str, ai_enhanced: bool = False) -> Dict:
        """
        格式化AI建议/问答
        用于旅行计划、零散问题等
        
        Args:
            suggestion_text: AI生成的建议文字
            ai_enhanced: 是否标记为AI生成
        """
        content = suggestion_text
        if ai_enhanced:
            content += "\n\n_💡 此建议由AI智能生成_"
        
        return {
            "action": "suggestion",
            "content": content,
            "data": None
        }
    
    # ==================== 辅助方法 ====================
    
    @staticmethod
    def _format_duration(duration: str) -> str:
        """
        格式化持续时间
        PT4H30M → 4h 30m
        """
        if not duration:
            return "未知"
        
        import re
        hours = re.search(r'(\d+)H', duration)
        minutes = re.search(r'(\d+)M', duration)
        
        result = ""
        if hours:
            result += f"{hours.group(1)}h "
        if minutes:
            result += f"{minutes.group(1)}m"
        
        return result.strip() or "未知"
    
    @staticmethod
    def _get_airline_name(carrier_code: str) -> str:
        """获取航空公司名称"""
        airline_names = {
            "CX": "Cathay Pacific",
            "JL": "Japan Airlines",
            "NH": "All Nippon Airways",
            "CA": "Air China",
            "CZ": "China Southern",
            "MU": "China Eastern",
            "HX": "Hong Kong Airlines",
            "KE": "Korean Air",
            "OZ": "Asiana Airlines",
            "SQ": "Singapore Airlines",
            "TG": "Thai Airways",
            # 可以继续添加
        }
        return airline_names.get(carrier_code, f"Airline {carrier_code}")
    
    @staticmethod
    def _get_ticketing_date() -> str:
        """获取出票截止日期（通常是明天）"""
        from datetime import date, timedelta
        tomorrow = date.today() + timedelta(days=1)
        return tomorrow.strftime("%Y-%m-%d")
    
    @staticmethod
    def _format_baggage(baggage_data: Any, cabin_class: str) -> str:
        """格式化行李额度"""
        if isinstance(baggage_data, int):
            return f"{baggage_data}件 (23KG)"
        
        # 根据舱位返回标准值
        if cabin_class == "BUSINESS":
            return "3件 (32KG)"
        elif cabin_class == "FIRST":
            return "3件 (32KG)"
        else:  # ECONOMY
            return "2件 (23KG)"
    
    @staticmethod
    def _get_default_amenities(carrier_code: str, cabin_class: str) -> List[Dict]:
        """获取默认设施（当API不返回时）"""
        if cabin_class == "BUSINESS":
            return [
                {"service": "全程 Wi-Fi", "isChargeable": False},
                {"service": "机上正餐", "isChargeable": False},
                {"service": "平躺座椅", "isChargeable": False}
            ]
        elif cabin_class == "FIRST":
            return [
                {"service": "全程 Wi-Fi", "isChargeable": False},
                {"service": "米其林餐食", "isChargeable": False},
                {"service": "私人套房", "isChargeable": False}
            ]
        else:  # ECONOMY
            return [
                {"service": "高速 Wi-Fi", "isChargeable": True},
                {"service": "机上正餐", "isChargeable": False},
                {"service": "USB 充电口", "isChargeable": False}
            ]
    
    @staticmethod
    def _get_weather_icon(description: str) -> str:
        """根据天气描述返回图标名"""
        desc_lower = description.lower()
        
        if '晴' in desc_lower or 'sunny' in desc_lower or 'clear' in desc_lower:
            return "sunny"
        elif '云' in desc_lower or 'cloud' in desc_lower:
            return "cloudy"
        elif '雨' in desc_lower or 'rain' in desc_lower:
            return "rainy"
        elif '雪' in desc_lower or 'snow' in desc_lower:
            return "snowy"
        else:
            return "sunny"


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例：格式化航班数据
    sample_flight_data = {
        'success': True,
        'data': [{
            'id': 'fl_001',
            'departure': {'iataCode': 'HKG', 'at': '2025-11-20T09:00:00'},
            'arrival': {'iataCode': 'NRT', 'at': '2025-11-20T14:30:00'},
            'carrierCode': 'CX',
            'number': '504',
            'aircraft': 'A350-900',
            'duration': 'PT4H30M',
            'cabinClass': 'ECONOMY',
            'price': {'total': '450.50', 'base': '400.00', 'currency': 'USD'}
        }],
        'count': 1
    }
    
    formatter = ResponseFormatter()
    result = formatter.format_flights(sample_flight_data, "飞往东京的")
    
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
