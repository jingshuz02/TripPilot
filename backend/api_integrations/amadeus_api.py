import requests
from datetime import date
from typing import Dict, Any, List
from backend.database.operations import FlightOperations
from backend.database.operations import HotelOperations
from backend.utils.data_processor import FlightDataProcessor
from backend.utils.data_processor import HotelDataProcessor
from .api_config import APIConfig


class AmadeusTravelService:
    def __init__(self, db_session):
        self.config = APIConfig()
        self.base_url = "https://test.api.amadeus.com"
        # 初始化航班相关
        self.flight_ops = FlightOperations(db_session)
        self.flight_data_processor = FlightDataProcessor()

        # 初始化酒店相关
        self.hotel_ops = HotelOperations(db_session)
        self.hotel_data_processor = HotelDataProcessor()

    def _get_headers(self) -> Dict[str, str]:
        """动态获取请求头，包含有效的访问令牌"""
        access_token = self.config.get_amadeus_token()
        if not access_token:
            raise Exception("无法获取有效的Amadeus访问令牌")

        return {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

    def search_and_save_flights(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """搜索航班并保存到数据库 - 这是核心业务逻辑"""
        try:
            # 1. 调用Amadeus API搜索航班
            flight_data = self._call_flights_api(search_params)

            if 'error' in flight_data:
                return {"success": False, "error": flight_data['error']}

            # 2. 验证数据
            validation_errors = self.data_processor.validate_flight_data(flight_data)
            if validation_errors:
                return {"success": False, "error": "数据验证失败", "details": validation_errors}

            # 3. 转换数据
            processed_data = self.data_processor.transform_flight_data(flight_data)

            # 4. 保存到数据库
            save_result = self.flight_ops.save_flight_offers(processed_data, search_params)

            if save_result['success']:
                return {
                    "success": True,
                    "flight_ids": save_result['flight_ids'],
                    "saved_count": save_result['saved_count'],
                    "search_id": f"{search_params.get('origin')}-{search_params.get('destination')}-{search_params.get('departure_date')}"
                }
            else:
                return {"success": False, "error": save_result['error']}

        except Exception as e:
            return {"success": False, "error": f"Amadeus服务错误: {str(e)}"}

    def _call_flights_api(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """调用Amadeus API搜索航班 - 专门的航班参数处理"""
        endpoint = f"{self.base_url}/v2/shopping/flight-offers"

        params = {
            "originLocationCode": search_params.get('origin'),
            "destinationLocationCode": search_params.get('destination'),
            "departureDate": search_params.get('departure_date'),
            "returnDate": search_params.get('return_date'),  # 往返日期
            "adults": search_params.get('adults', 1),
            "children": search_params.get('children', 0),  # 儿童数量
            "infants": search_params.get('infants', 0),  # 婴儿数量
            "includedAirlineCodes": search_params.get('included_airlines'),  # 包含的航空公司
            "excludedAirlineCodes": search_params.get('excluded_airlines'),  # 排除的航空公司
            "currencyCode": search_params.get('currency', 'USD'),  # 货币代码，默认USD
            "maxPrice": search_params.get('max_price'),  # 最高价格
            "travelClass": search_params.get('travel_class', 'ECONOMY'),
            "nonStop": str(search_params.get('non_stop', True)).lower(),
            "max": search_params.get('max_results', 10)
        }

        # 移除值为None的参数，避免API调用出错
        params = {k: v for k, v in params.items() if v is not None}

        return self._call_amadeus_api_generic(endpoint, params)

    def _call_amadeus_api_generic(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """通用Amadeus API调用方法"""
        try:
            headers = self._get_headers()

            print(f"🔍 调试信息:")
            print(f"   URL: {endpoint}")
            print(f"   参数: {params}")
            print(f"   使用令牌: {headers['Authorization'][:20]}...")

            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            print(f"📡 响应状态码: {response.status_code}")

            # 如果令牌过期，尝试刷新一次
            if response.status_code == 401:
                print("🔄 令牌可能过期，尝试刷新令牌...")
                self.config.access_token = None
                headers = self._get_headers()
                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                print(f"🔄 重试后状态码: {response.status_code}")

            response.raise_for_status()
            result = response.json()
            print(f"✅ API调用成功")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Amadeus API请求错误: {e}")
            if hasattr(e, 'response') and e.response is not None:
                error_text = e.response.text
                print(f"🔍 错误响应内容: {error_text}")
            return {"error": str(e)}

    def search_and_save_hotels(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """完整酒店搜索流程：基本信息 → 房态报价 → 评价"""
        try:
            # 步骤1: 搜索酒店基本信息
            print("🏨 步骤1: 搜索酒店基本信息...")
            hotel_data = self._call_hotels_api(search_params)
            
            if 'error' in hotel_data:
                return {"success": False, "error": hotel_data['error']}

            # 验证和保存基本信息
            validation_errors = self.hotel_data_processor.validate_hotel_data(hotel_data)
            if validation_errors:
                return {"success": False, "error": "酒店数据验证失败", "details": validation_errors}

            processed_data = self.hotel_data_processor.transform_hotel_data(hotel_data)
            save_result = self.hotel_ops.save_hotels(processed_data, search_params)

            if not save_result['success']:
                return {"success": False, "error": save_result['error']}

            hotel_ids = save_result['hotel_ids']
            print(f"✅ 保存了 {len(hotel_ids)} 个酒店的基本信息")

            # 步骤2: 查询酒店房态和报价
            print("💰 步骤2: 查询酒店房态和报价...")
            offers_result = self._search_and_save_hotel_offers(hotel_ids, search_params)

            # 步骤3: 查询酒店评价
            print("⭐ 步骤3: 查询酒店评价...")
            sentiments_result = self._search_and_save_hotel_sentiments(hotel_ids)

            return {
                "success": True,
                "hotel_ids": hotel_ids,
                "basic_saved": save_result['saved_count'],
                "offers_saved": offers_result.get('saved_count', 0),
                "sentiments_saved": sentiments_result.get('saved_count', 0),
                "search_id": f"hotel-{search_params.get('latitude')}-{search_params.get('longitude')}-{search_params.get('radius')}"
            }

        except Exception as e:
            return {"success": False, "error": f"酒店服务错误: {str(e)}"}

    def _search_and_save_hotel_offers(self, hotel_ids: List[str], search_params: Dict[str, Any]) -> Dict[str, Any]:
        """搜索并保存酒店报价信息 - 逐个处理避免无效ID影响"""
        if not hotel_ids:
            return {"success": True, "saved_count": 0}

        try:
            all_offers_data = {"data": []}
            successful_hotel_ids = []

            # 逐个处理酒店ID，避免一个无效ID影响整批查询
            for hotel_id in hotel_ids:
                print(f"🔍 查询酒店报价: {hotel_id}")
                try:
                    offers_data = self._call_hotel_offers_api(hotel_id, search_params)

                    if 'error' not in offers_data and 'data' in offers_data:
                        all_offers_data['data'].extend(offers_data['data'])
                        successful_hotel_ids.append(hotel_id)
                    else:
                        print(f"⚠️  跳过无效酒店ID: {hotel_id}")

                except Exception as e:
                    print(f"⚠️  查询酒店 {hotel_id} 报价失败: {e}")
                    continue

            # 保存报价信息
            if all_offers_data['data']:
                save_result = self.hotel_ops.save_hotel_offers(all_offers_data, search_params)
                print(f"✅ 保存了 {save_result.get('saved_count', 0)} 个酒店报价")
                return save_result
            else:
                return {"success": True, "saved_count": 0}

        except Exception as e:
            print(f"❌ 酒店报价查询错误: {e}")
            return {"success": False, "error": str(e)}

    def _search_and_save_hotel_sentiments(self, hotel_ids: List[str]) -> Dict[str, Any]:
        """搜索并保存酒店评价信息 - 逐个处理避免数量限制"""
        if not hotel_ids:
            return {"success": True, "saved_count": 0}

        try:
            all_sentiments_data = {"data": []}

            # 逐个处理酒店评价查询（评价API有严格的数量限制）
            for hotel_id in hotel_ids:
                print(f"🔍 查询酒店评价: {hotel_id}")
                try:
                    sentiments_data = self._call_hotel_sentiments_api(hotel_id)

                    if 'error' not in sentiments_data and 'data' in sentiments_data:
                        all_sentiments_data['data'].extend(sentiments_data['data'])
                    else:
                        print(f"⚠️  酒店 {hotel_id} 无评价数据")

                    # 添加延迟避免API限制
                    import time
                    time.sleep(0.5)

                except Exception as e:
                    print(f"⚠️  查询酒店 {hotel_id} 评价失败: {e}")
                    continue

            # 保存评价信息
            if all_sentiments_data['data']:
                save_result = self.hotel_ops.save_hotel_sentiments(all_sentiments_data)
                print(f"✅ 保存了 {save_result.get('saved_count', 0)} 个酒店评价")
                return save_result
            else:
                return {"success": True, "saved_count": 0}

        except Exception as e:
            print(f"❌ 酒店评价查询错误: {e}")
            return {"success": True, "saved_count": 0}


        return self._call_amadeus_api_generic(endpoint, params)

    def _call_hotel_offers_api(self, hotel_ids: str, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """调用酒店报价API"""
        endpoint = f"{self.base_url}/v3/shopping/hotel-offers"
        today = date.today().strftime('%Y-%m-%d')
        params = {
            "hotelIds": hotel_ids,
            "adults": search_params.get('adults', 1),
            "checkInDate": search_params.get('check_in_date', today),
            "checkOutDate": search_params.get('check_out_date'),
            "roomQuantity": search_params.get('room_quantity', 1),
            "countryOfResidence": search_params.get('country_of_residence'),
            "priceRange": search_params.get('price_range'),
            "currency": search_params.get('currency'),
            "boardType": search_params.get('board_type'),
            "includeClosed": search_params.get('include_closed'),
            "paymentPolicy": search_params.get('payment_policy', 'NONE'),
            "bestRateOnly": str(search_params.get('best_rate_only', True)).lower(),
            "lang": search_params.get('lang', 'en')
        }

        # 移除值为None的参数
        params = {k: v for k, v in params.items() if v is not None}

        return self._call_amadeus_api_generic(endpoint, params)

    def _call_hotel_sentiments_api(self, hotel_ids: str) -> Dict[str, Any]:
        """调用酒店评价API"""
        endpoint = f"{self.base_url}/v2/e-reputation/hotel-sentiments"

        params = {
            "hotelIds": hotel_ids
        }

        return self._call_amadeus_api_generic(endpoint, params)
    def _call_hotels_api(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """调用Amadeus API搜索酒店 - 专门的酒店参数处理"""
        endpoint = f"{self.base_url}/v1/reference-data/locations/hotels/by-geocode"

        params = {
            "latitude": search_params.get('latitude'),
            "longitude": search_params.get('longitude'),
            "cityCode": search_params.get('cityCode'),
            "radius": search_params.get('radius', 5),
            "radiusUnit": search_params.get('radiusUnit', 'KM'),
            "chainCodes": search_params.get('chainCodes'),
            "hotelSource": search_params.get('hotelSource', 'ALL'),
            "ratings": search_params.get('ratings'),  # 例如: "3,4,5"
            "amenities": search_params.get('amenities'),  # 例如: "SWIMMING_POOL,SPA"
        }

        # 移除值为None的参数
        params = {k: v for k, v in params.items() if v is not None}

        return self._call_amadeus_api_generic(endpoint, params)