import requests
import json
from typing import Dict, Any, List
from backend.database.operations import FlightOperations
from backend.utils.data_processor import FlightDataProcessor
from .api_config import APIConfig


class AmadeusFlightService:
    def __init__(self, db_session):
        self.config = APIConfig()
        self.base_url = "https://test.api.amadeus.com"
        self.flight_ops = FlightOperations(db_session)
        self.data_processor = FlightDataProcessor()
        # 移除固定的headers，在每次请求时动态获取令牌

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
            flight_data = self._call_amadeus_api(search_params)

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

    def _call_amadeus_api(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """调用Amadeus API搜索航班"""
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
            "max": search_params.get('max_results', 5)
        }

        # 移除值为None的参数，避免API调用出错
        params = {k: v for k, v in params.items() if v is not None}

        try:
            # 动态获取headers
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
                # 强制清除缓存，重新获取令牌
                self.config.access_token = None
                headers = self._get_headers()

                response = requests.get(endpoint, headers=headers, params=params, timeout=30)
                print(f"🔄 重试后状态码: {response.status_code}")

            response.raise_for_status()

            result = response.json()
            print(result)
            data_count = len(result.get('data', []))
            print(f"✅ API调用成功，返回数据条数: {data_count}")
            return result

        except requests.exceptions.RequestException as e:
            print(f"❌ Amadeus API请求错误: {e}")
            if hasattr(e, 'response') and e.response is not None:
                error_text = e.response.text
                print(f"🔍 错误响应内容: {error_text}")

                # 尝试解析错误信息
                try:
                    error_data = json.loads(error_text)
                    if 'errors' in error_data:
                        error_detail = error_data['errors'][0]
                        return {
                            "error": f"{error_detail.get('title', 'API错误')}: {error_detail.get('detail', '未知错误')}"}
                except:
                    pass

            return {"error": str(e)}
        except Exception as e:
            print(f"🚨 其他错误: {e}")
            return {"error": f"API调用异常: {str(e)}"}



