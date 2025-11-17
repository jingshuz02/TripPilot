# backend/api_integrations/serper_api.py
import requests
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from backend.api_integrations.api_config import APIConfig
from backend.database.operations import save_search_result, save_to_cache, get_from_cache


class SerperAPI:
    def __init__(self):
        self.config = APIConfig()
        self.api_key = self.config.serper_api_key
        self.base_url = "https://google.serper.dev/search"

    def search(self, query: str, num_results: int = 10, intent_type: str = "general", location: str = "") -> Dict[str, Any]:
        """General search - with caching and database storage"""
        try:
            # First try to get from cache
            cached_result = get_from_cache(query, intent_type, location)
            if cached_result:
                print(f"♻️ Using cached results: {query}")
                return cached_result

            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "q": query,
                "num": num_results
            }

            print(f"🔍 Serper search [{intent_type}]: {query}")
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()

            result = response.json()
            processed_result = self._process_results(result, query, intent_type, location)

            # Save to database and cache
            self._save_search_data(query, intent_type, location, processed_result)

            print(f"✅ Serper search successful, returned {len(processed_result.get('organic', []))} results")
            return processed_result

        except requests.exceptions.RequestException as e:
            error_msg = f"Serper API request error: {e}"
            print(f"❌ {error_msg}")
            return self._create_error_response(error_msg)
        except Exception as e:
            error_msg = f"Serper search exception: {e}"
            print(f"❌ {error_msg}")
            return self._create_error_response(error_msg)

    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "error": error_message,
            "organic": [],
            "knowledge_graph": {},
            "related_searches": [],
            "search_timestamp": datetime.now().isoformat(),
            "success": False
        }

    def _save_search_data(self, query: str, intent_type: str, location: str, search_results: Dict[str, Any]):
        """Save search data to database and cache"""
        try:
            # Prepare data for saving
            save_data = {
                "query": query,
                "intent_type": intent_type,
                "location": location,
                "search_results": search_results,
                "result_count": len(search_results.get("organic", [])),
                "search_timestamp": search_results.get("search_timestamp")
            }

            # Save to database
            save_search_result(save_data)

            # Save to cache
            save_to_cache(query, intent_type, location, search_results)

        except Exception as e:
            print(f"⚠️ Failed to save search data: {e}")

    def search_by_intent(self, intent_type: str, location: str, **kwargs) -> Dict[str, Any]:
        """
        Search based on intent type

        Args:
            intent_type: Intent type (general/attractions/restaurants/guides/seasonal/transportation/accommodation/culture/shopping/nightlife)
            location: Location name
            **kwargs: Additional parameters
        """
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
        return handler(location, **kwargs)

    def _handle_general_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle general search"""
        query = kwargs.get('query', f"{location} travel information guide")
        return self.search(query, intent_type="general", location=location)

    def _handle_attractions_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle attractions search"""
        country = kwargs.get('country')
        query_suffix = kwargs.get('query_suffix', 'top attractions tourist spots')

        if country:
            query = f"{location} {country} {query_suffix}"
        else:
            query = f"{location} {query_suffix}"

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
        return self.search(query, num_results=12, intent_type="restaurants", location=location)

    def _handle_travel_guides_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle travel guides search"""
        days = kwargs.get('days')
        if days:
            query = f"{location} {days} days travel itinerary guide plan"
        else:
            query = f"{location} travel guide itinerary things to do"
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

        return self.search(query, num_results=8, intent_type="seasonal", location=location)

    def _handle_transportation_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle transportation search"""
        query = f"{location} transportation how to get around public transport"
        return self.search(query, num_results=8, intent_type="transportation", location=location)

    def _handle_accommodation_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle accommodation search"""
        area = kwargs.get('area')
        if area:
            query = f"{location} {area} best hotels accommodation where to stay"
        else:
            query = f"{location} best areas to stay hotels accommodation"
        return self.search(query, num_results=10, intent_type="accommodation", location=location)

    def _handle_cultural_info_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle cultural information search"""
        query = f"{location} culture customs etiquette local traditions"
        return self.search(query, num_results=8, intent_type="culture", location=location)

    def _handle_shopping_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle shopping search"""
        query = f"{location} shopping best places to shop markets malls"
        return self.search(query, num_results=8, intent_type="shopping", location=location)

    def _handle_nightlife_search(self, location: str, **kwargs) -> Dict[str, Any]:
        """Handle nightlife search"""
        query = f"{location} nightlife bars clubs entertainment"
        return self.search(query, num_results=6, intent_type="nightlife", location=location)

    def _process_results(self, raw_data: Dict[str, Any], query: str, intent_type: str, location: str = "") -> Dict[str, Any]:
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