from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
from database.db_init import init_database, get_session
from api_integrations.amadeus_api import AmadeusTravelService
from database.operations import get_search_history, get_search_statistics
from api_integrations.serper_api import search_with_intent
from datetime import datetime


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Initialize DeepSeek client
deepseek_client = Config.get_deepseek_client()


@app.route('/', methods=['GET'])
def home():
    """Root endpoint - API information"""
    return jsonify({
        "service": "TripPilot API",
        "version": "1.0",
        "endpoints": {
            "health": "/health [GET]",
            "chat": "/api/chat [POST]",
            "plan_trip": "/api/plan-trip [POST]"
        },
        "status": "running"
    })


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "TripPilot API",
        "llm": "DeepSeek"
    })


@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat interaction endpoint"""
    try:
        data = request.json
        user_message = data.get('message', '')
        conversation_history = data.get('history', [])

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Build conversation messages
        messages = [
            {
                "role": "system",
                "content": "You are TripPilot, a professional travel planning assistant. You help users plan trips, book hotels and flights, find attractions, and provide practical travel advice. Please respond in a friendly and professional tone."
            }
        ]

        # Add conversation history
        messages.extend(conversation_history)

        # Add current user message
        messages.append({"role": "user", "content": user_message})

        # Call DeepSeek API
        response = deepseek_client.chat.completions.create(
            model=Config.DEEPSEEK_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )

        assistant_message = response.choices[0].message.content

        return jsonify({
            "message": assistant_message,
            "status": "success",
            "model": Config.DEEPSEEK_MODEL
        })

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


@app.route('/api/plan-trip', methods=['POST'])
def plan_trip():
    """Dedicated trip planning endpoint"""
    try:
        data = request.json
        destination = data.get('destination', '')
        start_date = data.get('start_date', '')
        end_date = data.get('end_date', '')
        budget = data.get('budget', '')
        preferences = data.get('preferences', '')

        # Build planning request
        prompt = f"""Please plan a trip for me with the following details:
Destination: {destination}
Start Date: {start_date}
End Date: {end_date}
Budget: {budget} USD
Preferences: {preferences}

Please provide a detailed itinerary including:
1. Recommended attractions and activities
2. Accommodation suggestions
3. Transportation arrangements
4. Budget allocation
5. Important notes and tips"""

        response = deepseek_client.chat.completions.create(
            model=Config.DEEPSEEK_MODEL,
            messages=[
                {"role": "system",
                 "content": "You are a professional travel planner, skilled at creating detailed travel plans."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=3000
        )

        plan = response.choices[0].message.content

        return jsonify({
            "plan": plan,
            "status": "success"
        })

    except Exception as e:
        print(f"Error in plan_trip endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


# 404 错误处理
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint not found",
        "status": "error",
        "available_endpoints": {
            "home": "/ [GET]",
            "health": "/health [GET]",
            "chat": "/api/chat [POST]",
            "plan_trip": "/api/plan-trip [POST]"
        }
    }), 404


# 500 错误处理
@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Internal server error",
        "status": "error"
    }), 500


engine = init_database()
db_session = get_session(engine)
amadeus_service = AmadeusTravelService(db_session)
@app.route('/api/flights/search', methods=['POST'])
def search_flights():
    """搜索航班"""
    try:
        search_params = request.get_json()

        # 验证必要参数
        required_params = ['origin', 'destination', 'departure_date']
        for param in required_params:
            if not search_params.get(param):
                return jsonify({"error": f"缺少必要参数: {param}"}), 400

        db_session = get_session(engine)

        try:
            # 创建服务实例
            flight_service = AmadeusTravelService(db_session)

            # 调用服务处理
            result = flight_service.search_and_save_flights(search_params)
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 500

        finally:
            db_session.close()

    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500

@app.route('/api/hotels/search', methods=['POST'])
def search_hotels():
    """搜索酒店"""
    try:
        search_params = request.get_json()

        # 验证必要参数
        required_params = ['latitude', 'longitude']
        for param in required_params:
            if not search_params.get(param):
                return jsonify({"error": f"缺少必要参数: {param}"}), 400

        # 调用服务处理
        result = amadeus_service.search_and_save_hotels(search_params)

        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500

    except Exception as e:
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


@app.route('/api/search', methods=['POST'])
def search_endpoint():
    """
    搜索接口
    """
    try:
        data = request.get_json()

        if not data or 'location' not in data:
            return jsonify({
                "success": False,
                "error": "缺少必要参数: location"
            }), 400

        intent_type = data.get('intent_type', '通用')
        location = data.get('location')

        result = search_with_intent(
            intent_type=intent_type,
            location=location,
            query=data.get('query'),
            days=data.get('days'),
            cuisine=data.get('cuisine'),
            budget=data.get('budget'),
            season=data.get('season'),
            event_type=data.get('event_type'),
            area=data.get('area'),
            country=data.get('country')
        )

        response = {
            "success": True,
            "intent_type": intent_type,
            "location": location,
            "timestamp": datetime.now().isoformat(),
            "data": result
        }

        return jsonify(response)

    except Exception as e:
        print(f"❌ 搜索接口错误: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/search/history', methods=['GET'])
def get_search_history_endpoint():
    """
    获取搜索历史记录
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        history = get_search_history(limit=limit)

        return jsonify({
            "success": True,
            "data": history
        })

    except Exception as e:
        print(f"❌ 获取搜索历史失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500



if __name__ == '__main__':
    # Check API key before starting
    if not Config.DEEPSEEK_API_KEY:
        print("Warning: DEEPSEEK_API_KEY is not set!")
        print("Please set DEEPSEEK_API_KEY in your .env file")

    print("=" * 50)
    print("TripPilot API Server Starting...")
    print("=" * 50)
    print(f"Server running on: http://localhost:5000")
    print(f"Health check: http://localhost:5000/health")
    print(f"API Info: http://localhost:5000/")
    print("=" * 50)

    app.run(debug=Config.DEBUG, port=5000, host='0.0.0.0')