"""
TripPilot Flask API - 连接Streamlit前端
提供统一的聊天接口

运行方法:
    python flask_app.py

"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend.agent.travel_agent import TravelAgent
import traceback

# 初始化Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 初始化Agent
print("🚀 初始化TripPilot Agent...")
agent = TravelAgent()
print("✅ Agent初始化完成！")


# ==================== API端点 ====================

@app.route('/health', methods=['GET'])
def health_check():
    """
    健康检查端点
    前端用这个检查后端是否在线

    Returns:
        {"status": "ok", "message": "TripPilot后端运行正常"}
    """
    return jsonify({
        "status": "ok",
        "message": "TripPilot后端运行正常"
    }), 200


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    统一聊天接口
    接收前端的用户需求和偏好，返回统一格式的响应

    Request Body:
        {
            "prompt": "用户输入的文本",
            "preferences": {
                "budget": 1000,
                "start_date": "2025-12-01",
                "end_date": "2025-12-05",
                ...
            }
        }

    Returns:
        {
            "action": "search_flights/search_hotels/get_weather/suggestion",
            "content": "描述性文字",
            "data": [...] 或 null
        }
    """
    try:
        # 获取请求数据
        data = request.json

        if not data:
            return jsonify({
                "action": "error",
                "content": "请求数据为空",
                "data": None
            }), 400

        prompt = data.get('prompt', '')
        preferences = data.get('preferences', {})

        if not prompt:
            return jsonify({
                "action": "error",
                "content": "用户输入不能为空",
                "data": None
            }), 400

        # 记录请求
        print(f"\n{'='*60}")
        print(f"📥 收到请求:")
        print(f"   用户输入: {prompt}")
        print(f"   偏好设置: {preferences}")
        print(f"{'='*60}")

        # 构建完整的用户消息（包含偏好信息）
        full_message = prompt

        # 如果有偏好设置，添加到消息中
        if preferences:
            pref_text = []
            if preferences.get('budget'):
                pref_text.append(f"预算${preferences['budget']}")
            if preferences.get('start_date') and preferences.get('end_date'):
                pref_text.append(f"日期{preferences['start_date']}至{preferences['end_date']}")
            if preferences.get('destination'):
                pref_text.append(f"目的地{preferences['destination']}")

            if pref_text:
                full_message += f" ({', '.join(pref_text)})"

        # 调用Agent处理
        response = agent.process(full_message)

        # 记录响应
        print(f"\n📤 返回响应:")
        print(f"   Action: {response.get('action')}")
        print(f"   Content: {response.get('content')[:100]}...")
        print(f"{'='*60}\n")

        return jsonify(response), 200

    except Exception as e:
        # 错误处理
        print(f"❌ 处理请求时出错: {e}")
        traceback.print_exc()

        return jsonify({
            "action": "error",
            "content": f"服务器错误: {str(e)}",
            "data": None
        }), 500


@app.route('/api/test', methods=['POST'])
def test_endpoint():
    """
    测试端点 - 用于调试
    """
    data = request.json
    print(f"📥 测试数据: {data}")

    return jsonify({
        "action": "suggestion",
        "content": f"测试成功！收到消息: {data.get('prompt', '')}",
        "data": None
    }), 200


# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({
        "action": "error",
        "content": "API端点不存在",
        "data": None
    }), 404


@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    return jsonify({
        "action": "error",
        "content": "服务器内部错误",
        "data": None
    }), 500


# ==================== 启动服务器 ====================

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 TripPilot后端服务启动中...")
    print("="*60)
    print("📍 地址: http://localhost:5000")
    print("💡 健康检查: http://localhost:5000/health")
    print("💡 聊天API: http://localhost:5000/api/chat")
    print("="*60 + "\n")

    # 启动Flask应用
    app.run(
        host='0.0.0.0',  # 允许外部访问
        port=5000,        # 端口5000（前端默认连接这个端口）
        debug=True        # 开发模式，自动重载
    )