import requests
import streamlit as st

class APIClient:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
    
    def check_health(self):
        """Check backend health status"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def send_travel_request(self, prompt, preferences):
        """
        Send user request and travel preferences to backend
        prompt: Text input from user
        preferences: Travel preferences from sidebar (budget, dates, etc.)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/travel/request",
                json={
                    "prompt": prompt,
                    "preferences": preferences  # Includes budget, departure/return dates, language, etc.
                },
                timeout=30
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"Failed to send request: {str(e)}")
            return None
    
    def search_hotels(self, city, check_in, check_out, budget=None):
        """Search for hotels based on criteria"""
        try:
            response = requests.post(
                f"{self.base_url}/api/hotels/search",
                json={
                    "city": city,
                    "check_in": check_in,
                    "check_out": check_out,
                    "budget": budget  # Optional: filter by budget
                },
                timeout=10
            )
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            st.error(f"Hotel search failed: {str(e)}")
            return None
    
    def book_hotel(self, hotel_id, trip_id):
        pass
    
    def search_flights(self):
        pass

    def search_schedule(self):
        pass

    def get_weather(self):
        pass
