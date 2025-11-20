"""
TripPilot - 智能旅行助手
主入口文件
"""

import streamlit as st
import sys
import os
from datetime import datetime
from uuid import uuid4

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="TripPilot - 智能旅行助手",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== 全局样式 ====================

st.markdown("""
<style>
    /* 主题色 */
    .stApp {
        background-color: #f8f9fa;
    }

    /* 聊天消息样式 */
    .stChatMessage {
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
    }

    /* 容器边框 */
    .element-container {
        border-radius: 8px;
    }

    /* 按钮样式 */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.3s;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    /* 指标卡片 */
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


# ==================== 全局状态初始化 ====================

def init_session_state():
    """初始化所有session state"""

    # 行程列表
    if "trips" not in st.session_state:
        st.session_state.trips = [{
            "name": "我的旅行计划",
            "desc": "自动创建的默认行程",
            "id": str(uuid4())[:8],
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "destination": "",
            "start_date": "",
            "end_date": ""
        }]

    # 订单列表
    if "orders" not in st.session_state:
        st.session_state.orders = []

    # 预算
    if "budget" not in st.session_state:
        st.session_state.budget = 5000

    # 当前支付信息
    if "current_payment" not in st.session_state:
        st.session_state.current_payment = None

    # 消息历史
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 目的地
    if "destination" not in st.session_state:
        st.session_state.destination = ""

    # 旅行日期
    if "start_date" not in st.session_state:
        st.session_state.start_date = ""

    if "end_date" not in st.session_state:
        st.session_state.end_date = ""

    # 预设酒店数据（用于演示）
    if "preset_hotels" not in st.session_state:
        st.session_state.preset_hotels = [
            {
                "name": "东京浅草寺酒店 (3晚)",
                "price": 450,
                "desc": "步行5分钟到景点，含早餐",
                "location": "东京",
                "rating": 4.5
            },
            {
                "name": "涩谷现代酒店 (2晚)",
                "price": 380,
                "desc": "近购物区，免费wifi",
                "location": "东京",
                "rating": 4.2
            },
            {
                "name": "东京湾度假村 (4晚)",
                "price": 620,
                "desc": "海景房，含三餐",
                "location": "东京",
                "rating": 4.8
            }
        ]


# 初始化
init_session_state()

# ==================== 主页面内容 ====================

st.title("✈️ TripPilot - 智能旅行助手")
st.caption("Powered by AI | 让旅行规划更简单")

# 欢迎信息
st.markdown("""
### 👋 欢迎使用 TripPilot！

我是您的专属AI旅行顾问，可以帮您：
- 🔍 **搜索航班和酒店** - 快速找到最合适的选项
- 🌤️ **查询天气信息** - 了解目的地天气状况  
- 📋 **规划行程** - 智能推荐旅行路线
- 💰 **管理预算** - 实时追踪旅行花费
""")

st.divider()

# 快速统计
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "当前预算",
        f"${st.session_state.budget}",
        delta=None
    )

with col2:
    total_spent = sum(o['price'] for o in st.session_state.orders)
    st.metric(
        "已花费",
        f"${total_spent:.2f}",
        delta=f"-{total_spent / st.session_state.budget * 100:.1f}%" if st.session_state.budget > 0 else None
    )

with col3:
    st.metric(
        "订单数",
        len(st.session_state.orders),
        delta=None
    )

with col4:
    st.metric(
        "行程数",
        len(st.session_state.trips),
        delta=None
    )

st.divider()

# 快速开始
st.markdown("### 🚀 快速开始")

col_a, col_b = st.columns(2)

with col_a:
    if st.button("💬 开始聊天", use_container_width=True, type="primary"):
        st.switch_page("pages/chat.py")

    st.caption("与AI助手对话，规划您的旅行")

with col_b:
    if st.button("📋 查看订单", use_container_width=True):
        st.switch_page("pages/order.py")

    st.caption("管理您的航班和酒店订单")

st.divider()

# 使用指南
with st.expander("📖 使用指南", expanded=False):
    st.markdown("""
    #### 如何使用 TripPilot？

    1. **开始聊天**
       - 点击"开始聊天"按钮进入聊天页面
       - 告诉我您的旅行需求，例如："帮我找香港到东京的航班"

    2. **查看推荐**
       - AI会为您搜索并展示航班/酒店选项
       - 您可以使用筛选功能找到最合适的选项

    3. **预订**
       - 点击"预订"按钮将项目添加到订单
       - 系统会自动追踪您的预算使用情况

    4. **管理订单**
       - 在"订单"页面查看所有预订
       - 可以确认、删除或导出订单

    #### 💡 提示
    - 您可以随时在侧边栏调整预算
    - 支持多个行程并行管理
    - 所有数据保存在当前会话中
    """)

# ==================== 侧边栏 ====================

with st.sidebar:
    st.header("⚙️ 系统设置")

    # 后端状态检查
    st.markdown("#### 🔌 后端连接")

    import requests

    try:
        response = requests.get("http://localhost:5000/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ 后端服务正常")
        else:
            st.error("❌ 后端服务异常")
    except:
        st.error("❌ 后端服务未启动")
        st.caption("请运行: `python app.py`")

    st.divider()

    # 快速设置
    st.markdown("#### 🎯 快速设置")

    # 目的地
    destination = st.text_input(
        "目的地",
        value=st.session_state.destination,
        placeholder="例如：东京"
    )
    if destination != st.session_state.destination:
        st.session_state.destination = destination

    # 旅行日期
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        start_date = st.date_input(
            "开始日期",
            value=datetime.now().date()
        )
    with col_date2:
        end_date = st.date_input(
            "结束日期",
            value=datetime.now().date()
        )

    st.session_state.start_date = str(start_date)
    st.session_state.end_date = str(end_date)

    st.divider()

    # 关于
    st.markdown("#### ℹ️ 关于")
    st.caption("""
    **TripPilot v1.0**  
    智能旅行规划助手  

    基于AI技术，提供航班、酒店搜索和行程规划服务。
    """)

    # 反馈
    if st.button("💬 提供反馈", use_container_width=True):
        st.info("感谢您的反馈！功能开发中...")

# ==================== 页脚 ====================

st.markdown("---")
st.caption("TripPilot © 2025 | Powered by Claude AI")