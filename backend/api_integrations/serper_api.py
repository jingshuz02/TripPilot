# backend/api_integrations/serper_api.py
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.api_integrations.api_config import APIConfig
from backend.database.operations import save_search_result


class SerperAPI:
    def __init__(self):
        self.config = APIConfig()
        self.api_key = self.config.serper_api_key
        self.base_url = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = 10, intent_type: str = "general", location: str = "") -> Dict[
        str, Any]:
        """直接搜索，带数据库保存"""
        try:
            # 验证API密钥
            if not self.api_key:
                return self._create_error_response("Serper API密钥为空")

            if self.api_key == "your_serper_api_key_here":
                return self._create_error_response("请配置有效的Serper API密钥")

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "q": query,
                "num": num_results
            }

            print(f"🔍 Serper搜索调试信息:")
            print(f"  - API密钥: {self.api_key[:10]}...")
            print(f"  - 查询: {query}")
            print(f"  - 结果数: {num_results}")
            print(f"  - 请求URL: {self.base_url}")

            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )

            print(f"📡 响应状态码: {response.status_code}")

            # 详细的错误处理
            if response.status_code != 200:
                error_detail = response.text
                print(f"❌ API错误详情: {error_detail}")

                # 尝试解析错误信息
                try:
                    error_data = response.json()
                    error_msg = f"API错误 {response.status_code}: {error_data}"
                except:
                    error_msg = f"API错误 {response.status_code}: {error_detail}"

                return self._create_error_response(error_msg)

            # 解析成功响应
            result = response.json()
            print(f"✅ API响应解析成功")

            processed_result = self._process_results(result, query, intent_type, location)

            # 保存到数据库
            self._save_search_data(processed_result)

            print(f"✅ Serper搜索成功，返回 {len(processed_result.get('organic', []))} 条结果")
            return processed_result

        except requests.exceptions.RequestException as e:
            error_msg = f"Serper API请求错误: {e}"
            print(f"❌ {error_msg}")
            return self._create_error_response(error_msg)
        except Exception as e:
            error_msg = f"Serper搜索异常: {e}"
            print(f"❌ {error_msg}")
            return self._create_error_response(error_msg)

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """创建错误响应"""
        return {
            "error": error_message,
            "organic": [],
            "knowledge_graph": {},
            "related_searches": [],
            "search_timestamp": datetime.now().isoformat(),
            "success": False
        }

    def _save_search_data(self, search_results: Dict[str, Any]):
        """保存搜索数据到数据库"""
        try:
            # 准备保存数据
            save_data = {
                "query": search_results.get("query", ""),
                "intent_type": search_results.get("intent_type", "general"),
                "location": search_results.get("location", ""),
                "search_results": search_results,  # 保存整个处理后的结果
                "result_count": len(search_results.get("organic", [])),
                "search_timestamp": search_results.get("search_timestamp")
            }

            # 保存到数据库
            save_search_result(save_data)
            print(f"💾 搜索记录已保存到数据库: {save_data['query']}")

        except Exception as e:
            print(f"⚠️ 保存搜索数据失败: {e}")

    def search_by_intent(self, intent_type: str, location: str, **kwargs) -> Dict[str, Any]:
        """
        Search based on intent type

        Args:
            intent_type: Intent type (general/attractions/restaurants/guides/seasonal/transportation/accommodation/culture/shopping/nightlife)
            location: Location name
            **kwargs: Additional parameters
        """
        print(f"🎯 开始意图搜索:")
        print(f"  - 意图类型: {intent_type}")
        print(f"  - 地点: {location}")
        print(f"  - 额外参数: {kwargs}")

        intent_handlers = {
            "general": self._handle_general_search,
            "attractions": self._handle_attractions_search,
            "restaurants": self._handle_restaurants_search,
            "guides": self._handle_travel_guides_search,
            "seasonal": self._handle_seasonal_info_search,
            "transportation": self._handle_transportation_search,
            "accommodation": self._handle_accommodation_search,
            "culture": self._handle_cultural_info_search,
            "shopping": self._handle_shopping_search,
            "nightlife": self._handle_nightlife_search
        }

        handler = intent_handlers.get(intent_type, self._handle_general_search)
        print(f"  - 使用处理器: {handler.__name__}")

        result = handler(location, **kwargs)
        return result

    def _handle_general_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle general search"""
        query = kwargs.get('query', f"{location} travel information guide")
        print(f"🔍 生成通用查询: {query}")
        return self.search(query, intent_type="general", location=location)

    def _handle_attractions_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle attractions search"""
        country = kwargs.get('country')
        query_suffix = kwargs.get('query_suffix', 'top attractions tourist spots')

        if country:
            query = f"{location} {country} {query_suffix}"
        else:
            query = f"{location} {query_suffix}"

        print(f"🏯 生成景点查询: {query}")
        return self.search(query, num_results=15, intent_type="attractions", location=location)

    def _handle_restaurants_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle restaurants search"""
        cuisine = kwargs.get('cuisine')
        budget = kwargs.get('budget')
        query_parts = [f"{location} best restaurants"]

        if cuisine:
            query_parts.append(cuisine)
        if budget:
            query_parts.append(f"{budget} budget")
        if not cuisine and not budget:
            query_parts.append("local food popular")

        query = " ".join(query_parts)
        print(f"🍣 生成餐厅查询: {query}")
        return self.search(query, num_results=12, intent_type="restaurants", location=location)

    def _handle_travel_guides_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle travel guides search"""
        days = kwargs.get('days')
        if days:
            query = f"{location} {days} days travel itinerary guide plan"
        else:
            query = f"{location} travel guide itinerary things to do"
        print(f"🗺️ 生成攻略查询: {query}")
        return self.search(query, num_results=10, intent_type="guides", location=location)

    def _handle_seasonal_info_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle seasonal information search"""
        season = kwargs.get('season')
        event_type = kwargs.get('event_type')

        if event_type:
            query = f"{location} {event_type} time schedule dates 2024"
        elif season:
            query = f"{location} {season} season best time to visit weather events"
        else:
            query = f"{location} best time to visit seasonal events festivals"

        print(f"🌸 生成季节信息查询: {query}")
        return self.search(query, num_results=8, intent_type="seasonal", location=location)

    def _handle_transportation_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle transportation search"""
        query = f"{location} transportation how to get around public transport"
        print(f"🚇 生成交通查询: {query}")
        return self.search(query, num_results=8, intent_type="transportation", location=location)

    def _handle_accommodation_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle accommodation search"""
        area = kwargs.get('area')
        if area:
            query = f"{location} {area} best hotels accommodation where to stay"
        else:
            query = f"{location} best areas to stay hotels accommodation"
        print(f"🏨 生成住宿查询: {query}")
        return self.search(query, num_results=10, intent_type="accommodation", location=location)

    def _handle_cultural_info_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle cultural information search"""
        query = f"{location} culture customs etiquette local traditions"
        print(f"🎎 生成文化查询: {query}")
        return self.search(query, num_results=8, intent_type="culture", location=location)

    def _handle_shopping_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle shopping search"""
        query = f"{location} shopping best places to shop markets malls"
        print(f"🛍️ 生成购物查询: {query}")
        return self.search(query, num_results=8, intent_type="shopping", location=location)

    def _handle_nightlife_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle nightlife search"""
        query = f"{location} nightlife bars clubs entertainment"
        print(f"🌃 生成夜生活查询: {query}")
        return self.search(query, num_results=6, intent_type="nightlife", location=location)

    def _process_results(self, raw_data: Dict[str, Any], query: str, intent_type: str, location: str = "") -> Dict[
        str, Any]:
        """Process search results"""
        processed = {
            "success": True,
            "search_parameters": raw_data.get("searchParameters", {}),
            "organic": [],
            "knowledge_graph": raw_data.get("knowledgeGraph", {}),
            "related_searches": raw_data.get("relatedSearches", []),
            "people_also_ask": raw_data.get("peopleAlsoAsk", []),
            "query": query,
            "intent_type": intent_type,
            "location": location,
            "search_timestamp": datetime.now().isoformat(),
            "total_results": len(raw_data.get("organic", []))
        }

        # Process organic search results
        for item in raw_data.get("organic", []):
            processed_item = {
                "title": item.get("title", ""),
                "link": item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "position": item.get("position", 0),
                "date": item.get("date", ""),
                "displayed_link": item.get("displayedLink", "")
            }
            processed["organic"].append(processed_item)

        return processed

    def extract_key_information(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key information"""
        organic = search_results.get("organic", [])
        knowledge_graph = search_results.get("knowledge_graph", {})

        key_info = {
            "top_results": [],
            "summary": knowledge_graph.get("description", ""),
            "total_results": len(organic),
            "categories": []
        }

        # Extract key information from top 5 results
        for i, result in enumerate(organic[:5]):
            key_info["top_results"].append({
                "rank": i + 1,
                "title": result.get("title", ""),
                "summary": result.get("snippet", ""),
                "source": result.get("link", ""),
                "displayed_link": result.get("displayed_link", "")
            })

        return key_info


# Convenience function
def search_with_intent(intent_type: str, location: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function: Search based on intent

    Args:
        intent_type: Intent type
        location: Location
        **kwargs: Additional parameters

    Returns:
        Search results
    """
    api = SerperAPI()
    return api.search_by_intent(intent_type, location, **kwargs)