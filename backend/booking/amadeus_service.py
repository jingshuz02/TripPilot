"""
Amadeus API服务 - 完整AI增强版
处理航班和酒店搜索，包含AI增强功能补充缺失数据

"""
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import re

from config.config import Config


class AmadeusService:
    """
    Amadeus旅行服务（完整AI增强版）
    提供航班和酒店搜索功能，智能补充缺失数据
    """

    def __init__(self, deepseek_client=None):
        """初始化Amadeus服务"""
        # API配置
        self.client_id = Config.AMADEUS_CLIENT_ID
        self.client_secret = Config.AMADEUS_CLIENT_SECRET
        self.base_url = "https://test.api.amadeus.com"

        # Token管理
        self.access_token = None
        self.token_expires_at = None

        # AI增强
        self.deepseek_client = deepseek_client

        print("✅ Amadeus服务初始化完成（AI增强）")

    # ==================== 航班搜索（AI增强版）====================

    def search_flights(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        搜索航班（AI增强版）
        自动补充缺失的航班信息
        """
        try:
            origin = params['origin']
            destination = params['destination']
            date = params['departure_date']

            print(f"\n✈️  搜索航班: {origin} → {destination} ({date})")

            # 调用真实API
            endpoint = f"{self.base_url}/v2/shopping/flight-offers"

            api_params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": date,
                "adults": params.get('adults', 1),
                "travelClass": params.get('travel_class', 'ECONOMY'),
                "nonStop": str(params.get('non_stop', False)).lower(),
                "currencyCode": "USD",
                "max": params.get('max_results', 10)
            }

            result = self._call_api(endpoint, api_params)

            if 'error' in result:
                return {
                    'success': False,
                    'data': [],
                    'count': 0,
                    'message': f"搜索失败: {result['error']}"
                }

            # 提取并增强航班数据
            flights = result.get('data', [])
            enhanced_flights = []
            ai_enhanced_count = 0

            for flight in flights:
                enhanced_flight, is_ai_enhanced = self._enhance_flight_data(flight)
                enhanced_flights.append(enhanced_flight)
                if is_ai_enhanced:
                    ai_enhanced_count += 1

            print(f"✅ 找到 {len(enhanced_flights)} 个航班")
            if ai_enhanced_count > 0:
                print(f"   💡 AI增强了 {ai_enhanced_count} 个航班的数据")

            return {
                'success': True,
                'data': enhanced_flights,
                'count': len(enhanced_flights),
                'ai_enhanced_count': ai_enhanced_count,
                'message': f"找到 {len(enhanced_flights)} 个航班"
            }

        except KeyError as e:
            return {
                'success': False,
                'data': [],
                'count': 0,
                'message': f"缺少必要参数: {e}"
            }
        except Exception as e:
            print(f"❌ 航班搜索错误: {e}")
            return {
                'success': False,
                'data': [],
                'count': 0,
                'message': f"搜索错误: {str(e)}"
            }

    def _enhance_flight_data(self, flight: Dict) -> tuple:
        """
        增强航班数据，补充缺失字段

        Returns:
            (enhanced_flight, is_ai_enhanced)
        """
        try:
            itinerary = flight.get('itineraries', [{}])[0]
            segments = itinerary.get('segments', [])

            if not segments:
                return flight, False

            first_segment = segments[0]
            last_segment = segments[-1]

            # 获取舱位和行李信息
            traveler_pricing = flight.get('travelerPricings', [{}])[0]
            fare_details = traveler_pricing.get('fareDetailsBySegment', [{}])[0]
            cabin_class = fare_details.get('cabin', 'ECONOMY')

            # 基础数据
            enhanced = {
                'id': flight.get('id'),
                'source': flight.get('source', 'GDS'),
                'price': {
                    'total': flight.get('price', {}).get('total'),
                    'base': flight.get('price', {}).get('base'),
                    'currency': flight.get('price', {}).get('currency', 'USD'),
                    'grandTotal': flight.get('price', {}).get('grandTotal')
                },
                'departure': {
                    'iataCode': first_segment.get('departure', {}).get('iataCode'),
                    'terminal': first_segment.get('departure', {}).get('terminal'),
                    'at': first_segment.get('departure', {}).get('at')
                },
                'arrival': {
                    'iataCode': last_segment.get('arrival', {}).get('iataCode'),
                    'terminal': last_segment.get('arrival', {}).get('terminal'),
                    'at': last_segment.get('arrival', {}).get('at')
                },
                'carrierCode': first_segment.get('carrierCode'),
                'number': first_segment.get('number'),
                'aircraft': first_segment.get('aircraft', {}).get('code'),
                'duration': itinerary.get('duration'),
                'numberOfStops': len(segments) - 1,
                'cabinClass': cabin_class  # 从API返回的数据中获取
            }

            # 检查缺失字段并AI补充
            is_ai_enhanced = False
            missing_fields = []

            # 检查关键字段
            if not enhanced.get('aircraft'):
                missing_fields.append('aircraft')
            if not enhanced['departure'].get('terminal'):
                missing_fields.append('departure_terminal')
            if not enhanced['arrival'].get('terminal'):
                missing_fields.append('arrival_terminal')

            # 获取行李额度
            enhanced['includedCheckedBags'] = fare_details.get('includedCheckedBags', {}).get('quantity')
            enhanced['cabin'] = cabin_class

            if not enhanced.get('includedCheckedBags'):
                missing_fields.append('baggage')

            # 如果有缺失字段且有AI客户端，使用AI补充
            if missing_fields and self.deepseek_client:
                ai_data = self._ai_enhance_flight(enhanced, missing_fields)
                if ai_data:
                    enhanced.update(ai_data)
                    enhanced['_ai_enhanced'] = True
                    enhanced['_ai_fields'] = missing_fields
                    is_ai_enhanced = True

            return enhanced, is_ai_enhanced

        except Exception as e:
            print(f"⚠️  航班数据增强失败: {e}")
            return flight, False

    def _ai_enhance_flight(self, flight_data: Dict, missing_fields: List[str]) -> Optional[Dict]:
        """使用AI补充缺失的航班信息"""
        if not self.deepseek_client:
            return None

        try:
            carrier = flight_data.get('carrierCode', '')
            aircraft_code = flight_data.get('aircraft', '')
            cabin_class = flight_data.get('cabinClass', 'ECONOMY')

            prompt = f"""为航班补充缺失信息。
航班: {carrier}{flight_data.get('number', '')}
机型: {aircraft_code if aircraft_code else '未知'}
舱位: {cabin_class}

缺失字段: {', '.join(missing_fields)}

返回JSON格式，只包含缺失字段的合理值：
{{
    "aircraft": "机型代码（如B787-8、A350-900）",
    "departure_terminal": "航站楼（如T1、T2或null）",
    "arrival_terminal": "航站楼",
    "includedCheckedBags": "托运行李件数（1-3）",
    "amenities": [
        {{"service": "服务名", "isChargeable": true/false}}
    ]
}}

注意：
- 如果机型已知就保持，如果未知则根据航司和航线推测
- 行李额度要符合舱位标准（经济舱1-2件，商务舱2-3件）
- 设施要符合机型和航司特点

只返回JSON，不要其他内容。"""

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # 低温度保证准确性
                max_tokens=500
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)

            if json_match:
                ai_data = json.loads(json_match.group())
                print(f"   💡 AI补充了字段: {', '.join(missing_fields)}")
                return ai_data

            return None

        except Exception as e:
            print(f"⚠️  AI增强失败: {e}")
            return None

    # ==================== 酒店搜索（已有AI增强）====================

    def search_hotels(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        搜索酒店（带AI增强）
        （保持原来的实现，已经有AI增强）
        """
        try:
            lat = params['latitude']
            lon = params['longitude']
            check_in = params['check_in_date']
            check_out = params['check_out_date']

            print(f"\n🏨 搜索酒店: ({lat}, {lon})")
            print(f"   日期: {check_in} → {check_out}")

            # 步骤1: 搜索酒店基本信息
            hotels = self._search_hotels_basic(params)

            if not hotels:
                return {
                    'success': False,
                    'hotels': [],
                    'offers': [],
                    'reviews': [],
                    'count': 0,
                    'ai_enhanced': False,
                    'message': '未找到酒店'
                }

            print(f"✅ 找到 {len(hotels)} 个酒店")

            # 步骤2: 获取房间报价（真实API + AI补充）
            offers, ai_offer_count = self._get_hotel_offers(hotels, params)
            print(f"   💰 获取了 {len(offers)} 个报价 (AI生成: {ai_offer_count})")

            # 步骤3: 获取酒店评价（真实API + AI补充）
            reviews, ai_review_count = self._get_hotel_reviews(hotels)
            print(f"   ⭐ 获取了 {len(reviews)} 个评价 (AI生成: {ai_review_count})")

            ai_enhanced = ai_offer_count > 0 or ai_review_count > 0

            return {
                'success': True,
                'hotels': hotels,
                'offers': offers,
                'reviews': reviews,
                'count': len(hotels),
                'ai_enhanced': ai_enhanced,
                'message': f"找到 {len(hotels)} 个酒店"
            }

        except Exception as e:
            print(f"❌ 酒店搜索错误: {e}")
            return {
                'success': False,
                'hotels': [],
                'offers': [],
                'reviews': [],
                'count': 0,
                'ai_enhanced': False,
                'message': f"搜索错误: {str(e)}"
            }

    def _search_hotels_basic(self, params: Dict) -> List[Dict]:
        """搜索酒店基本信息"""
        endpoint = f"{self.base_url}/v1/reference-data/locations/hotels/by-geocode"

        api_params = {
            "latitude": params['latitude'],
            "longitude": params['longitude'],
            "radius": params.get('radius', 5),
            "radiusUnit": "KM"
        }

        result = self._call_api(endpoint, api_params)
        return result.get('data', []) if 'error' not in result else []

    def _get_hotel_offers(self, hotels: List[Dict], params: Dict) -> tuple:
        """获取酒店报价（真实API + AI补充）"""
        all_offers = []
        ai_count = 0

        for hotel in hotels[:5]:
            hotel_id = hotel.get('hotelId')

            endpoint = f"{self.base_url}/v3/shopping/hotel-offers"
            api_params = {
                "hotelIds": hotel_id,
                "checkInDate": params.get('check_in_date'),
                "checkOutDate": params.get('check_out_date'),
                "adults": params.get('adults', 2),
                "bestRateOnly": "true"
            }

            result = self._call_api(endpoint, api_params)

            if 'data' in result and result['data']:
                all_offers.extend(result['data'])
            else:
                if self.deepseek_client:
                    ai_offer = self._generate_hotel_offer(hotel, params)
                    if ai_offer:
                        all_offers.append(ai_offer)
                        ai_count += 1

        return all_offers, ai_count

    def _get_hotel_reviews(self, hotels: List[Dict]) -> tuple:
        """获取酒店评价（真实API + AI补充）"""
        all_reviews = []
        ai_count = 0

        for hotel in hotels[:5]:
            hotel_id = hotel.get('hotelId')

            endpoint = f"{self.base_url}/v2/e-reputation/hotel-sentiments"
            api_params = {"hotelIds": hotel_id}

            result = self._call_api(endpoint, api_params)

            if 'data' in result and result['data']:
                all_reviews.extend(result['data'])
            else:
                if self.deepseek_client:
                    ai_review = self._generate_hotel_review(hotel)
                    if ai_review:
                        all_reviews.append(ai_review)
                        ai_count += 1

        return all_reviews, ai_count

    def _generate_hotel_offer(self, hotel: Dict, params: Dict) -> Optional[Dict]:
        """使用AI生成酒店报价"""
        if not self.deepseek_client:
            return None

        try:
            hotel_id = hotel.get('hotelId')
            hotel_name = hotel.get('name', 'Hotel')

            prompt = f"""为酒店生成合理的房间报价（演示数据）。
酒店: {hotel_name}
入住: {params.get('check_in_date')}
退房: {params.get('check_out_date')}

返回JSON：
{{
    "room_type": "房型名称",
    "price": 每晚价格USD（100-400）,
    "description": "30字描述"
}}

只返回JSON。"""

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=300
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)

            if json_match:
                ai_data = json.loads(json_match.group())
                return {
                    "type": "hotel-offers",
                    "hotel": {"hotelId": hotel_id, "name": hotel_name},
                    "available": True,
                    "offers": [{
                        "id": f"ai-{hotel_id}-{int(datetime.now().timestamp())}",
                        "checkInDate": params.get('check_in_date'),
                        "checkOutDate": params.get('check_out_date'),
                        "room": {
                            "type": ai_data['room_type'],
                            "description": {"text": ai_data['description']}
                        },
                        "price": {
                            "currency": "USD",
                            "total": str(ai_data['price']),
                            "base": str(ai_data['price'])
                        },
                        "_source": "ai_generated"
                    }]
                }

            return None

        except Exception as e:
            print(f"⚠️  AI生成报价失败: {e}")
            return None

    def _generate_hotel_review(self, hotel: Dict) -> Optional[Dict]:
        """使用AI生成酒店评价"""
        if not self.deepseek_client:
            return None

        try:
            hotel_id = hotel.get('hotelId')

            prompt = f"""生成酒店评价数据。
返回JSON：
{{
    "overall_rating": 60-95,
    "number_of_reviews": 80-300,
    "sleep_quality": 60-95,
    "service": 60-95,
    "facilities": 60-95,
    "location": 60-95
}}

只返回JSON。"""

            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200
            )

            result_text = response.choices[0].message.content
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)

            if json_match:
                ai_data = json.loads(json_match.group())
                return {
                    "type": "hotelSentiment",
                    "hotelId": hotel_id,
                    "overallRating": ai_data['overall_rating'],
                    "numberOfReviews": ai_data['number_of_reviews'],
                    "sentiments": {
                        "sleepQuality": ai_data['sleep_quality'],
                        "service": ai_data['service'],
                        "facilities": ai_data['facilities'],
                        "location": ai_data['location']
                    },
                    "_source": "ai_generated"
                }

            return None

        except Exception as e:
            print(f"⚠️  AI生成评价失败: {e}")
            return None

    # ==================== Token管理 ====================

    def _get_amadeus_token(self) -> str:
        """获取Amadeus访问令牌"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        print("🔑 获取Amadeus令牌...")

        url = f"{self.base_url}/v1/security/oauth2/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        try:
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data['access_token']

            expires_in = token_data.get('expires_in', 1799)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)

            print("✅ 令牌获取成功")
            return self.access_token

        except Exception as e:
            raise Exception(f"无法获取Amadeus令牌: {str(e)}")

    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        access_token = self._get_amadeus_token()
        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def _call_api(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """通用API调用"""
        try:
            headers = self._get_headers()
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)

            if response.status_code == 401:
                print("🔄 Token过期，重新获取...")
                self.access_token = None
                headers = self._get_headers()
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"❌ API请求错误: {e}")
            return {"error": str(e)}