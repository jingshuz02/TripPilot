# """
# TripPilot Flask后端服务 - 改进版
# 提供API接口供前端调用
# """

# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import sys
# import os

# # 添加父目录到路径
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# # 导入TravelAgent
# from agent.travel_agent import TravelAgent

# # 初始化Flask应用
# app = Flask(__name__)
# CORS(app)  # 允许跨域请求

# # 初始化Agent（全局实例）
# agent = TravelAgent()

# @app.route('/health', methods=['GET'])
# def health_check():
#     """健康检查端点"""
#     return jsonify({
#         "status": "healthy",
#         "service": "TripPilot Backend",
#         "version": "2.0"
#     }), 200

# @app.route('/api/chat', methods=['POST'])
# def chat():
#     """
#     聊天API端点

#     请求格式:
#     {
#         "prompt": "用户消息",
#         "preferences": {
#             "budget": 5000,
#             "destination": "成都",
#             "start_date": "2024-01-01",
#             "end_date": "2024-01-03"
#         },
#         "conversation_history": []  # 可选
#     }
#     """
#     try:
#         data = request.json

#         # 获取请求数据
#         user_prompt = data.get('prompt', '')
#         preferences = data.get('preferences', {})
#         history = data.get('conversation_history', [])

#         print("=" * 60)
#         print("📥 收到请求:")
#         print(f"   用户输入: {user_prompt}")
#         print(f"   偏好设置: {preferences}")
#         print("=" * 60)

#         # 更新Agent的对话历史
#         if history:
#             agent.conversation_history = history

#         # 处理消息
#         response = agent.process_message(user_prompt, preferences)

#         print("\n📤 返回响应:")
#         print(f"   Action: {response.get('action')}")
#         print(f"   Content: {response.get('content', '')[:100]}...")
#         print("=" * 60 + "\n")

#         return jsonify(response), 200

#     except Exception as e:
#         print(f"❌ 处理请求时出错: {e}")
#         return jsonify({
#             "action": "error",
#             "content": f"处理请求时出错: {str(e)}",
#             "data": None,
#             "suggestions": ["重试", "检查输入", "联系支持"]
#         }), 500

# @app.route('/api/search/hotels', methods=['POST'])
# def search_hotels():
#     """搜索酒店API"""
#     try:
#         data = request.json
#         destination = data.get('destination', '')
#         checkin = data.get('checkin_date')
#         checkout = data.get('checkout_date')
#         budget = data.get('budget', 5000)

#         # 调用Agent处理酒店搜索
#         message = f"在{destination}搜索酒店，入住{checkin}，退房{checkout}"
#         preferences = {
#             "destination": destination,
#             "budget": budget,
#             "start_date": checkin,
#             "end_date": checkout
#         }

#         response = agent.process_message(message, preferences)

#         return jsonify(response), 200

#     except Exception as e:
#         print(f"❌ 搜索酒店失败: {e}")
#         return jsonify({
#             "error": str(e),
#             "data": []
#         }), 500

# @app.route('/api/search/flights', methods=['POST'])
# def search_flights():
#     """搜索航班API"""
#     try:
#         data = request.json
#         origin = data.get('origin', '')
#         destination = data.get('destination', '')
#         departure_date = data.get('departure_date')
#         return_date = data.get('return_date')

#         # 调用Agent处理航班搜索
#         message = f"查找从{origin}到{destination}的航班，{departure_date}出发"
#         if return_date:
#             message += f"，{return_date}返回"

#         preferences = {
#             "origin": origin,
#             "destination": destination,
#             "start_date": departure_date,
#             "end_date": return_date
#         }

#         response = agent.process_message(message, preferences)

#         return jsonify(response), 200

#     except Exception as e:
#         print(f"❌ 搜索航班失败: {e}")
#         return jsonify({
#             "error": str(e),
#             "data": []
#         }), 500

# @app.route('/api/weather', methods=['POST'])
# def get_weather():
#     """获取天气信息API"""
#     try:
#         data = request.json
#         city = data.get('city', '')

#         # 调用Agent处理天气查询
#         message = f"{city}的天气怎么样？"
#         preferences = {"destination": city}

#         response = agent.process_message(message, preferences)

#         return jsonify(response), 200

#     except Exception as e:
#         print(f"❌ 获取天气失败: {e}")
#         return jsonify({
#             "error": str(e),
#             "data": None
#         }), 500

# @app.route('/api/plan/trip', methods=['POST'])
# def plan_trip():
#     """规划完整行程API"""
#     try:
#         data = request.json
#         destination = data.get('destination', '')
#         days = data.get('days', 3)
#         budget = data.get('budget', 5000)
#         interests = data.get('interests', [])

#         # 构建详细的规划请求
#         message = f"帮我规划一个{destination}{days}天的旅行，预算{budget}元"
#         if interests:
#             message += f"，我喜欢{', '.join(interests)}"

#         preferences = {
#             "destination": destination,
#             "days": days,
#             "budget": budget,
#             "interests": interests
#         }

#         response = agent.process_message(message, preferences)

#         return jsonify(response), 200

#     except Exception as e:
#         print(f"❌ 行程规划失败: {e}")
#         return jsonify({
#             "error": str(e),
#             "data": None
#         }), 500

# if __name__ == '__main__':
#     print("\n" + "=" * 60)
#     print("🚀 TripPilot后端服务启动中...")
#     print("=" * 60)
#     print("📍 地址: http://localhost:5000")
#     print("💡 健康检查: http://localhost:5000/health")
#     print("💡 聊天API: http://localhost:5000/api/chat")
#     print("=" * 60 + "\n")

#     # 启动Flask服务
#     app.run(
#         host='0.0.0.0',
#         port=5000,
#         debug=True
#     )


"""
TripPilot Flask Backend Service - Improved Version
Provides API endpoints for frontend calls.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import TravelAgent
from agent.travel_agent import TravelAgent

# Initialize Flask Application
app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Requests

# Initialize Agent (Global Instance)
agent = TravelAgent()

@app.route('/health', methods=['GET'])
def health_check():
    """Health Check Endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TripPilot Backend",
        "version": "2.0"
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Chat API Endpoint

    Request Format:
    {
        "prompt": "User message",
        "preferences": {
            "budget": 5000,
            "destination": "Chengdu",
            "start_date": "2024-01-01",
            "end_date": "2024-01-03"
        },
        "conversation_history": []  # Optional
    }
    """
    try:
        data = request.json

        # Get request data
        user_prompt = data.get('prompt', '')
        preferences = data.get('preferences', {})
        history = data.get('conversation_history', [])

        print("=" * 60)
        print("📥 Request Received:")
        print(f"   User Input: {user_prompt}")
        print(f"   Preferences: {preferences}")
        print("=" * 60)

        # Update Agent's conversation history
        if history:
            agent.conversation_history = history

        # Process message
        response = agent.process_message(user_prompt, preferences)

        print("\n📤 Sending Response:")
        print(f"   Action: {response.get('action')}")
        print(f"   Content: {response.get('content', '')[:100]}...")
        print("=" * 60 + "\n")

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Error processing request: {e}")
        return jsonify({
            "action": "error",
            "content": f"Error processing request: {str(e)}",
            "data": None,
            "suggestions": ["Retry", "Check input", "Contact support"]
        }), 500

@app.route('/api/search/hotels', methods=['POST'])
def search_hotels():
    """Search Hotels API"""
    try:
        data = request.json
        destination = data.get('destination', '')
        checkin = data.get('checkin_date')
        checkout = data.get('checkout_date')
        budget = data.get('budget', 5000)

        # Call Agent to handle hotel search
        message = f"Search hotels in {destination}, check-in {checkin}, check-out {checkout}"
        preferences = {
            "destination": destination,
            "budget": budget,
            "start_date": checkin,
            "end_date": checkout
        }

        response = agent.process_message(message, preferences)

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Failed to search hotels: {e}")
        return jsonify({
            "error": str(e),
            "data": []
        }), 500

@app.route('/api/search/flights', methods=['POST'])
def search_flights():
    """Search Flights API"""
    try:
        data = request.json
        origin = data.get('origin', '')
        destination = data.get('destination', '')
        departure_date = data.get('departure_date')
        return_date = data.get('return_date')

        # Call Agent to handle flight search
        message = f"Find flights from {origin} to {destination}, departing {departure_date}"
        if return_date:
            message += f", returning {return_date}"

        preferences = {
            "origin": origin,
            "destination": destination,
            "start_date": departure_date,
            "end_date": return_date
        }

        response = agent.process_message(message, preferences)

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Failed to search flights: {e}")
        return jsonify({
            "error": str(e),
            "data": []
        }), 500

@app.route('/api/weather', methods=['POST'])
def get_weather():
    """Get Weather Information API"""
    try:
        data = request.json
        city = data.get('city', '')

        # Call Agent to handle weather query
        message = f"What is the weather like in {city}?"
        preferences = {"destination": city}

        response = agent.process_message(message, preferences)

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Failed to get weather: {e}")
        return jsonify({
            "error": str(e),
            "data": None
        }), 500

@app.route('/api/plan/trip', methods=['POST'])
def plan_trip():
    """Plan Complete Itinerary API"""
    try:
        data = request.json
        destination = data.get('destination', '')
        days = data.get('days', 3)
        budget = data.get('budget', 5000)
        interests = data.get('interests', [])

        # Build detailed planning request
        message = f"Help me plan a {days}-day trip to {destination} with a budget of ¥{budget}"
        if interests:
            message += f", I like {', '.join(interests)}"

        preferences = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests
        }

        response = agent.process_message(message, preferences)

        return jsonify(response), 200

    except Exception as e:
        print(f"❌ Itinerary planning failed: {e}")
        return jsonify({
            "error": str(e),
            "data": None
        }), 500

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🚀 TripPilot Backend Service Starting...")
    print("=" * 60)
    print("📍 Address: http://localhost:5000")
    print("💡 Health Check: http://localhost:5000/health")
    print("💡 Chat API: http://localhost:5000/api/chat")
    print("=" * 60 + "\n")

    # Start Flask service
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )