from typing import Dict, Any, List
import json


class FlightDataProcessor:
    """航班数据处理工具"""

    @staticmethod
    def validate_flight_data(flight_data: Dict[str, Any]) -> List[str]:
        """验证航班数据完整性"""
        errors = []

        if not flight_data.get('data'):
            errors.append("缺少航班数据")
            return errors

        required_fields = ['id', 'itineraries', 'price']

        for i, flight in enumerate(flight_data.get('data', [])):
            for field in required_fields:
                if not flight.get(field):
                    errors.append(f"航班 {i + 1} 缺少必要字段: {field}")

            # 验证行程信息
            itineraries = flight.get('itineraries', [])
            if not itineraries:
                errors.append(f"航班 {flight.get('id')} 缺少行程信息")
            else:
                segments = itineraries[0].get('segments', [])
                if not segments:
                    errors.append(f"航班 {flight.get('id')} 缺少航段信息")

        return errors

    @staticmethod
    def transform_flight_data(flight_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换航班数据格式"""
        # 这里可以添加数据清洗和转换逻辑
        processed_data = flight_data.copy()

        # 示例：确保价格字段为数值类型
        for flight in processed_data.get('data', []):
            price = flight.get('price', {})
            if price:
                for key in ['total', 'base', 'grandTotal']:
                    if key in price and isinstance(price[key], str):
                        try:
                            price[key] = float(price[key])
                        except ValueError:
                            price[key] = 0.0

        return processed_data

    @staticmethod
    def extract_key_information(flight_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取关键航班信息"""
        key_info = []

        for flight in flight_data.get('data', []):
            itinerary = flight['itineraries'][0] if flight.get('itineraries') else {}
            segment = itinerary.get('segments', [{}])[0] if itinerary.get('segments') else {}
            price = flight.get('price', {})

            info = {
                'id': flight.get('id'),
                'departure': segment.get('departure', {}).get('iataCode'),
                'arrival': segment.get('arrival', {}).get('iataCode'),
                'departure_time': segment.get('departure', {}).get('at'),
                'arrival_time': segment.get('arrival', {}).get('at'),
                'carrier': segment.get('carrierCode'),
                'flight_number': segment.get('number'),
                'total_price': price.get('total'),
                'currency': price.get('currency'),
                'duration': itinerary.get('duration')
            }
            key_info.append(info)

        return key_info



class HotelDataProcessor:
    def validate_hotel_data(self, hotel_data: Dict[str, Any]) -> List[str]:
        """验证酒店数据"""
        errors = []

        if 'data' not in hotel_data:
            errors.append("缺少data字段")
            return errors

        hotels = hotel_data.get('data', [])
        for i, hotel in enumerate(hotels):
            if not hotel.get('hotelId'):
                errors.append(f"第{i}个酒店缺少hotelId")
            if not hotel.get('name'):
                errors.append(f"第{i}个酒店缺少name")

        return errors

    def transform_hotel_data(self, hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """转换酒店数据格式"""
        # 这里可以对数据进行清洗和转换
        return hotel_data

    def extract_key_information(self, hotel_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取关键酒店信息"""
        hotels = hotel_data.get('data', [])
        key_info = []

        for hotel in hotels:
            info = {
                'hotel_id': hotel.get('hotelId'),
                'name': hotel.get('name'),
                'rating': hotel.get('rating'),
                'city': hotel.get('address', {}).get('cityName'),
                'distance': hotel.get('distance', {}).get('value'),
                'distance_unit': hotel.get('distance', {}).get('unit'),
                'latitude': hotel.get('geoCode', {}).get('latitude'),
                'longitude': hotel.get('geoCode', {}).get('longitude')
            }
            key_info.append(info)

        return key_info

    def analyze_hotels(self, hotel_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析酒店数据"""
        key_info = self.extract_key_information(hotel_data)

        if not key_info:
            return {"analysis": "无有效酒店数据"}

        ratings = [hotel['rating'] for hotel in key_info if hotel.get('rating')]
        distances = [hotel['distance'] for hotel in key_info if hotel.get('distance')]
        cities = [hotel['city'] for hotel in key_info if hotel.get('city')]

        analysis = {
            "total_hotels": len(key_info),
            "rating_range": {
                "min": min(ratings) if ratings else 0,
                "max": max(ratings) if ratings else 0,
                "average": sum(ratings) / len(ratings) if ratings else 0
            },
            "distance_range": {
                "min": min(distances) if distances else 0,
                "max": max(distances) if distances else 0,
                "average": sum(distances) / len(distances) if distances else 0
            },
            "cities": list(set(cities)),
            "highest_rated": max(key_info, key=lambda x: x.get('rating', 0)) if key_info else None,
            "closest_hotel": min(key_info, key=lambda x: x.get('distance', float('inf'))) if key_info else None
        }

        return analysis