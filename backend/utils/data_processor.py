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