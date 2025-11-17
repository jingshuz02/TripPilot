from flask import Flask, request, jsonify, current_app
from flask_cors import CORS
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import Config
from backend.maps.weather_api import WeatherAPI
from backend.maps.gaode_maps import GaodeMapAPI
app = Flask(__name__)
app.json.ensure_ascii = False
app.config.from_object(Config)
from backend.agent.travel_agent import TravelAgent
CORS(app)

# Initialize DeepSeek client
deepseek_client = Config.get_deepseek_client()

agent = TravelAgent()
@app.route('/api/agent/chat', methods=['POST'])
def smart_chat():
    """智能代理处理复杂查询"""
    data = request.json
    message = data.get('message')

    # 让代理处理（自动调用需要的工具）
    response = agent.process_message(message)

    return jsonify({"message": response, "status": "success"})

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

# --------实时天气---------
# /api/weather/current?city=上海
@app.route('/api/weather/current', methods=['GET'])
def get_current_weather():
    """
    高德实时天气接口
    参数: ?city=城市名称/行政区编码
    返回: JSON
    """
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"code": 400, "msg": "缺少 city 参数"}), 400

    try:
        api = WeatherAPI()
        data = api.get_current_weather(city)
        return jsonify({"code": 0, "data": data, "msg": "success"})
    except ValueError as ve:          # 参数非法
        current_app.logger.warning(f"天气参数错误: {ve}")
        return jsonify({"code": 400, "msg": str(ve)}), 400
    except RuntimeError as re:        # 高德返回业务异常
        current_app.logger.error(f"高德天气异常: {re}")
        return jsonify({"code": 500, "msg": str(re)}), 500
    except Exception as e:            # 兜底
        current_app.logger.exception("天气接口未知异常")
        return jsonify({"code": 500, "msg": "internal error"}), 500

# --------- 天气预报 ---------
# /api/weather/forecast?city=上海&days=3
@app.route('/api/weather/forecast', methods=['GET'])
def get_forecast():
    """
    高德未来 4 天天气预报
    参数:
        city: 城市名称/行政区编码（必填）
        days: 需要几天，默认 4，最大 4（可选）
    """
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"code": 400, "msg": "缺少 city 参数"}), 400

    try:
        days = int(request.args.get("days", 4))
        if not 1 <= days <= 4:
            raise ValueError("days 只能取 1-4")
    except ValueError as e:
        return jsonify({"code": 400, "msg": f"days 参数非法: {e}"}), 400

    try:
        api = WeatherAPI()
        data = api.get_forecast(city, days=days)
        return jsonify({"code": 0, "data": data, "msg": "success"})
    except ValueError as ve:
        current_app.logger.warning(f"天气预报参数错误: {ve}")
        return jsonify({"code": 400, "msg": str(ve)}), 400
    except RuntimeError as re:
        current_app.logger.error(f"高德预报异常: {re}")
        return jsonify({"code": 500, "msg": str(re)}), 500
    except Exception as e:
        current_app.logger.exception("预报接口未知异常")
        return jsonify({"code": 500, "msg": "internal error"}), 500


# -------------------gaodemaps-----------------------
gaode = GaodeMapAPI()
# ------- 统一响应 -------
def ok(data): return jsonify({"code": 0, "data": data})
def fail(msg): return jsonify({"code": 1, "msg": str(msg)})

# ------- 地图接口 -------
# /api/map/search?city=北京&keyword=北京大学
@app.route("/api/map/search", methods=["GET"])
def search_place():
    city = request.args.get("city")
    keyword = request.args.get("keyword")
    if not city or not keyword:
        return fail("缺少 city / keyword")
    try:
        return ok(gaode.search_place(city, keyword))
    except Exception as e:
        return fail(e)

# /api/map/route?origin=116.481,39.990&destination=116.434,39.908&mode=driving/walking(只支持这两种)
@app.route("/api/map/route", methods=["GET"])
def plan_route():
    orig = request.args.get("origin")
    dest = request.args.get("destination")
    mode = request.args.get("mode", "driving")
    if not orig or not dest:
        return fail("缺少 origin / destination")
    try:
        return ok(gaode.plan_route(orig, dest, mode))
    except Exception as e:
        return fail(e)

# /api/map/distance?origins=116.481,39.990|116.45,39.95&destination=116.434,39.908(&mode=driving)&batch=1
# 加mode是沿路距离，不加是直线距离
@app.route("/api/map/distance", methods=["GET"])
def calc_distance():
    origins = request.args.get("origins")
    destination = request.args.get("destination")
    batch = request.args.get("batch") == "1"
    mode = request.args.get("mode")  # 新增
    if not origins or not destination:
        return fail("缺少 origins / destination")
    try:
        return ok(gaode.calculate_distance(origins, destination, mode, batch))
    except Exception as e:
        return fail(e)

# /api/map/regeo?location=116.30539,39.99925
@app.route("/api/map/regeo", methods=["GET"])
def regeo():
    location = request.args.get("location")
    if not location:
        return fail("缺少 location")
    try:
        return ok(gaode.regeo(location))
    except Exception as e:
        return fail(e)

# /api/map/geo?address=北京大学
@app.route("/api/map/geo", methods=["GET"])
def geo():
    address = request.args.get("address")
    city = request.args.get("city")
    if not address:
        return fail("缺少 address")
    try:
        return ok(gaode.geo(address, city))
    except Exception as e:
        return fail(e)

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