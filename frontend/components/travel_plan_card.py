"""
美化版旅行计划展示组件 - 纯绿色主题
特点：
1. 纯绿色配色方案
2. 无emoji，纯文字+图标
3. 精美的渐变背景
4. 现代化卡片设计
5. 流畅的动画效果
"""

import streamlit as st
from datetime import datetime


def display_travel_plan(plan_data, message_id=0):
    """
    显示单个旅行计划方案 - 美化版

    参数:
        plan_data: 方案数据字典
        message_id: 消息ID（用于唯一key）
    """

    # 纯绿色主题CSS - 美化版
    st.markdown("""
    <style>
    /* 全局容器背景 */
    .plans-wrapper {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        padding: 24px;
        border-radius: 16px;
        margin: 16px 0;
    }
    
    /* 方案卡片 */
    .plan-card {
        background: linear-gradient(145deg, #ffffff 0%, #fafafa 100%);
        border: 1px solid #a5d6a7;
        border-radius: 16px;
        padding: 0;
        margin-bottom: 24px;
        box-shadow: 0 4px 16px rgba(76, 175, 80, 0.15);
        overflow: hidden;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .plan-card:hover {
        box-shadow: 0 8px 32px rgba(76, 175, 80, 0.25);
        transform: translateY(-4px);
        border-color: #66bb6a;
    }
    
    /* 方案头部 - 渐变背景 */
    .plan-header {
        background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%);
        padding: 32px 28px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    
    .plan-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 200px;
        height: 200px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 50%;
    }
    
    .plan-header::after {
        content: '';
        position: absolute;
        bottom: -30%;
        left: -10%;
        width: 150px;
        height: 150px;
        background: rgba(255, 255, 255, 0.08);
        border-radius: 50%;
    }
    
    .plan-title {
        font-size: 28px;
        font-weight: 700;
        margin: 0 0 8px 0;
        position: relative;
        z-index: 1;
        letter-spacing: -0.5px;
    }
    
    .plan-subtitle {
        font-size: 16px;
        opacity: 0.95;
        position: relative;
        z-index: 1;
        font-weight: 500;
    }
    
    /* 价格标签 */
    .price-section {
        background: rgba(255, 255, 255, 0.15);
        padding: 16px 28px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        backdrop-filter: blur(10px);
    }
    
    .price-badge {
        background: white;
        color: #2e7d32;
        padding: 12px 24px;
        border-radius: 24px;
        font-size: 24px;
        font-weight: 800;
        display: inline-flex;
        align-items: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        letter-spacing: -0.5px;
    }
    
    .price-label {
        color: white;
        font-size: 13px;
        opacity: 0.9;
        margin-right: 8px;
        font-weight: 500;
    }
    
    /* 内容区域 */
    .plan-content {
        padding: 28px;
    }
    
    /* 亮点标签 */
    .highlights-section {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        border-left: 4px solid #43a047;
        padding: 20px 24px;
        margin: 0 0 24px 0;
        border-radius: 0 8px 8px 0;
    }
    
    .highlights-title {
        color: #2e7d32;
        font-size: 15px;
        font-weight: 700;
        margin: 0 0 12px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .highlight-tags {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    
    .highlight-tag {
        background: white;
        color: #388e3c;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
        border: 1px solid #a5d6a7;
        transition: all 0.3s ease;
    }
    
    .highlight-tag:hover {
        background: #4caf50;
        color: white;
        border-color: #4caf50;
        transform: translateY(-2px);
    }
    
    /* 详情区域 */
    .details-section {
        background: linear-gradient(135deg, #fafafa 0%, #ffffff 100%);
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 0;
        margin-top: 20px;
        overflow: hidden;
    }
    
    .section-header {
        background: linear-gradient(135deg, #f1f8e9 0%, #e8f5e9 100%);
        padding: 16px 24px;
        border-bottom: 2px solid #c8e6c9;
    }
    
    .section-title {
        color: #2e7d32;
        font-size: 17px;
        font-weight: 700;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .section-content {
        padding: 24px;
    }
    
    /* 信息行 */
    .info-grid {
        display: grid;
        grid-template-columns: 140px 1fr;
        gap: 16px 24px;
        padding: 12px 0;
        border-bottom: 1px solid #f1f8e9;
    }
    
    .info-grid:last-child {
        border-bottom: none;
    }
    
    .info-label {
        color: #66bb6a;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
    }
    
    .info-label::before {
        content: '▸';
        color: #43a047;
        margin-right: 8px;
        font-weight: bold;
    }
    
    .info-value {
        color: #1b5e20;
        font-size: 15px;
        font-weight: 600;
    }
    
    /* 每日行程卡片 */
    .day-card {
        background: white;
        border: 1px solid #c8e6c9;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }
    
    .day-card:hover {
        border-color: #81c784;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.15);
    }
    
    .day-header {
        background: linear-gradient(135deg, #e8f5e9 0%, #f1f8e9 100%);
        color: #2e7d32;
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 15px;
        font-weight: 700;
        margin: -20px -20px 16px -20px;
        border-bottom: 2px solid #a5d6a7;
    }
    
    .activity-timeline {
        position: relative;
        padding-left: 32px;
    }
    
    .activity-timeline::before {
        content: '';
        position: absolute;
        left: 8px;
        top: 8px;
        bottom: 8px;
        width: 2px;
        background: linear-gradient(180deg, #66bb6a 0%, #a5d6a7 100%);
    }
    
    .activity-item {
        position: relative;
        padding: 10px 0;
        font-size: 14px;
        color: #2e7d32;
        line-height: 1.6;
    }
    
    .activity-item::before {
        content: '';
        position: absolute;
        left: -27px;
        top: 16px;
        width: 10px;
        height: 10px;
        background: #43a047;
        border: 2px solid white;
        border-radius: 50%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .activity-time {
        color: #66bb6a;
        font-weight: 700;
        margin-right: 12px;
        font-size: 13px;
    }
    
    .activity-desc {
        color: #388e3c;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 32px;
        font-weight: 600;
        font-size: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(67, 160, 71, 0.3);
        letter-spacing: 0.5px;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #388e3c 0%, #4caf50 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(67, 160, 71, 0.4);
    }
    
    /* 展开按钮特殊样式 */
    .expand-button {
        background: transparent;
        border: 2px solid #43a047;
        color: #43a047;
    }
    
    .expand-button:hover {
        background: #43a047;
        color: white;
    }
    
    /* 分隔线 */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, #a5d6a7 50%, transparent 100%);
        margin: 24px 0;
    }
    </style>
    """, unsafe_allow_html=True)

    plan_name = plan_data.get('plan_name', '旅行方案')
    total_cost = plan_data.get('total_cost', 0)
    destination = plan_data.get('destination', '目的地')
    days = plan_data.get('days', 3)
    highlights = plan_data.get('highlights', [])

    st.markdown("<div class='plan-card'>", unsafe_allow_html=True)

    # 方案头部
    st.markdown(f"""
    <div class='plan-header'>
        <div class='plan-title'>{plan_name}</div>
        <div class='plan-subtitle'>{destination} · {days}天行程</div>
    </div>
    """, unsafe_allow_html=True)

    # 价格和按钮区域
    st.markdown("<div class='price-section'>", unsafe_allow_html=True)

    col_price, col_btn = st.columns([2, 1])
    with col_price:
        st.markdown(f"""
        <div style='display: flex; align-items: center;'>
            <span class='price-label'>方案总价</span>
            <span class='price-badge'>¥{total_cost:,.0f}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_btn:
        plan_id = plan_data.get('plan_id', f'plan_{message_id}')
        if st.button("选择此方案", key=f"select_{plan_id}", type="primary", use_container_width=True):
            st.success(f"已选择方案：{plan_name}")
            st.session_state[f'selected_plan_{message_id}'] = plan_data
            st.balloons()
            return "selected"

    st.markdown("</div>", unsafe_allow_html=True)  # price-section

    # 内容区域
    st.markdown("<div class='plan-content'>", unsafe_allow_html=True)

    # 方案亮点
    if highlights:
        st.markdown("<div class='highlights-section'>", unsafe_allow_html=True)
        st.markdown("<div class='highlights-title'>方案亮点</div>", unsafe_allow_html=True)

        tags_html = "<div class='highlight-tags'>"
        for h in highlights:
            tags_html += f"<span class='highlight-tag'>{h}</span>"
        tags_html += "</div>"
        st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # 展开/收起详情
    plan_key = f"expand_plan_{plan_id}_{message_id}"
    if plan_key not in st.session_state:
        st.session_state[plan_key] = False

    col_expand1, col_expand2 = st.columns([1, 3])
    with col_expand1:
        if st.button(
            "收起详情" if st.session_state[plan_key] else "展开详情",
            key=f"{plan_key}_btn",
            use_container_width=True
        ):
            st.session_state[plan_key] = not st.session_state[plan_key]
            st.rerun()

    # 详情区域
    if st.session_state[plan_key]:
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # 航班信息
        flights = plan_data.get('flights', {})
        if flights:
            st.markdown("""
            <div class='details-section'>
                <div class='section-header'>
                    <div class='section-title'>航班信息</div>
                </div>
                <div class='section-content'>
            """, unsafe_allow_html=True)

            departure = flights.get('departure', {})
            if departure:
                st.markdown(f"""
                <div style='margin-bottom: 24px;'>
                    <div style='color: #388e3c; font-size: 14px; font-weight: 700; margin-bottom: 12px;'>去程航班</div>
                    <div class='info-grid'>
                        <div class='info-label'>航班号</div>
                        <div class='info-value'>{departure.get('flight_no', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>出发时间</div>
                        <div class='info-value'>{departure.get('departure_time', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>到达时间</div>
                        <div class='info-value'>{departure.get('arrival_time', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>票价</div>
                        <div class='info-value'>¥{departure.get('price', 0):,.0f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            return_flight = flights.get('return', {})
            if return_flight:
                st.markdown(f"""
                <div>
                    <div style='color: #388e3c; font-size: 14px; font-weight: 700; margin-bottom: 12px;'>返程航班</div>
                    <div class='info-grid'>
                        <div class='info-label'>航班号</div>
                        <div class='info-value'>{return_flight.get('flight_no', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>出发时间</div>
                        <div class='info-value'>{return_flight.get('departure_time', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>到达时间</div>
                        <div class='info-value'>{return_flight.get('arrival_time', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>票价</div>
                        <div class='info-value'>¥{return_flight.get('price', 0):,.0f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

        # 酒店信息
        hotels = plan_data.get('hotels', [])
        if hotels:
            st.markdown("""
            <div class='details-section'>
                <div class='section-header'>
                    <div class='section-title'>住宿安排</div>
                </div>
                <div class='section-content'>
            """, unsafe_allow_html=True)

            for hotel in hotels:
                st.markdown(f"""
                <div style='margin-bottom: 16px;'>
                    <div class='info-grid'>
                        <div class='info-label'>酒店名称</div>
                        <div class='info-value'>{hotel.get('name', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>位置</div>
                        <div class='info-value'>{hotel.get('location', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>入住日期</div>
                        <div class='info-value'>{hotel.get('check_in', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>退房日期</div>
                        <div class='info-value'>{hotel.get('check_out', 'N/A')}</div>
                    </div>
                    <div class='info-grid'>
                        <div class='info-label'>房费</div>
                        <div class='info-value'>¥{hotel.get('price_per_night', 0)}/晚 × {hotel.get('nights', 1)}晚 = ¥{hotel.get('total_price', 0):,.0f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

        # 每日行程
        daily_itinerary = plan_data.get('daily_itinerary', [])
        if daily_itinerary:
            st.markdown("""
            <div class='details-section'>
                <div class='section-header'>
                    <div class='section-title'>每日行程安排</div>
                </div>
                <div class='section-content'>
            """, unsafe_allow_html=True)

            for day_info in daily_itinerary:
                day_num = day_info.get('day', 1)
                date = day_info.get('date', '')
                activities = day_info.get('activities', [])

                st.markdown(f"""
                <div class='day-card'>
                    <div class='day-header'>第{day_num}天 · {date}</div>
                    <div class='activity-timeline'>
                """, unsafe_allow_html=True)

                for activity in activities:
                    time = activity.get('time', '')
                    desc = activity.get('description', '')
                    st.markdown(f"""
                    <div class='activity-item'>
                        <span class='activity-time'>{time}</span>
                        <span class='activity-desc'>{desc}</span>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("</div></div>", unsafe_allow_html=True)

            st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # plan-content
    st.markdown("</div>", unsafe_allow_html=True)  # plan-card

    return None


def display_travel_plans(plans_data, message_id=0):
    """
    显示多个旅行方案供用户选择 - 美化版

    参数:
        plans_data: 包含多个方案的列表
        message_id: 消息ID
    """
    if not plans_data:
        st.info("暂无旅行方案")
        return

    # 统计信息卡片
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #43a047 0%, #66bb6a 100%); 
                padding: 24px 32px; 
                border-radius: 12px; 
                margin-bottom: 24px;
                box-shadow: 0 4px 16px rgba(67, 160, 71, 0.25);'>
        <div style='color: white; font-size: 16px; font-weight: 500; margin-bottom: 8px;'>
            为您精心准备
        </div>
        <div style='color: white; font-size: 32px; font-weight: 800; letter-spacing: -1px;'>
            {len(plans_data)} 套完整旅行方案
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 显示每个方案
    st.markdown("<div class='plans-wrapper'>", unsafe_allow_html=True)

    for idx, plan in enumerate(plans_data):
        if 'plan_id' not in plan:
            plan['plan_id'] = f"plan_{message_id}_{idx}"

        result = display_travel_plan(plan, message_id=message_id)

        if result == "selected":
            st.info("您可以继续调整方案，或前往订单页面完成预订")

    st.markdown("</div>", unsafe_allow_html=True)


# 测试代码
if __name__ == "__main__":
    st.set_page_config(page_title="美化版旅行计划", layout="wide")

    st.title("美化版旅行计划组件")
    st.caption("纯绿色主题 · 无emoji · 精美设计")

    test_plans = [
        {
            'plan_name': '经济实惠方案',
            'plan_id': 'plan_eco',
            'total_cost': 2800,
            'destination': '武汉',
            'days': 5,
            'highlights': ['精选经济型酒店', '涵盖主要景点', '优化行程安排', '性价比超高'],
            'flights': {
                'departure': {
                    'flight_no': 'CZ3456',
                    'departure_time': '2025-11-30 08:30',
                    'arrival_time': '2025-11-30 10:15',
                    'price': 650
                },
                'return': {
                    'flight_no': 'CZ3457',
                    'departure_time': '2025-12-05 16:00',
                    'arrival_time': '2025-12-05 17:45',
                    'price': 680
                }
            },
            'hotels': [{
                'name': '武汉如家快捷酒店（江汉路店）',
                'location': '江汉路步行街',
                'check_in': '2025-11-30',
                'check_out': '2025-12-05',
                'nights': 5,
                'price_per_night': 198,
                'total_price': 990
            }],
            'daily_itinerary': [
                {
                    'day': 1,
                    'date': '2025-11-30',
                    'activities': [
                        {'time': '上午', 'description': '抵达武汉天河机场，专车接送至酒店办理入住'},
                        {'time': '下午', 'description': '酒店休息，适应当地气候和环境'},
                        {'time': '傍晚', 'description': '前往户部巷品尝武汉特色小吃'}
                    ]
                },
                {
                    'day': 2,
                    'date': '2025-12-01',
                    'activities': [
                        {'time': '09:00', 'description': '酒店享用早餐'},
                        {'time': '10:00', 'description': '游览黄鹤楼，登楼远眺长江美景'},
                        {'time': '12:30', 'description': '品尝地道武汉菜'},
                        {'time': '14:00', 'description': '参观湖北省博物馆，欣赏编钟表演'},
                        {'time': '18:00', 'description': '楚河汉街购物休闲'}
                    ]
                },
                {
                    'day': 3,
                    'date': '2025-12-02',
                    'activities': [
                        {'time': '09:00', 'description': '早餐后前往武汉大学'},
                        {'time': '10:00', 'description': '漫步武大校园，感受百年名校风采'},
                        {'time': '14:00', 'description': '游览昙华林文艺街区'},
                        {'time': '17:00', 'description': '江滩公园散步，欣赏长江日落'}
                    ]
                }
            ]
        },
        {
            'plan_name': '舒适品质方案',
            'plan_id': 'plan_comfort',
            'total_cost': 4200,
            'destination': '武汉',
            'days': 5,
            'highlights': ['四星级酒店', '深度游览', '特色美食', '舒适体验'],
            'flights': {
                'departure': {
                    'flight_no': 'MU2345',
                    'departure_time': '2025-11-30 09:00',
                    'arrival_time': '2025-11-30 10:45',
                    'price': 850
                },
                'return': {
                    'flight_no': 'MU2346',
                    'departure_time': '2025-12-05 15:00',
                    'arrival_time': '2025-12-05 16:45',
                    'price': 880
                }
            },
            'hotels': [{
                'name': '武汉君悦酒店',
                'location': '武汉国际广场',
                'check_in': '2025-11-30',
                'check_out': '2025-12-05',
                'nights': 5,
                'price_per_night': 458,
                'total_price': 2290
            }],
            'daily_itinerary': [
                {
                    'day': 1,
                    'date': '2025-11-30',
                    'activities': [
                        {'time': '上午', 'description': '抵达武汉，四星级酒店入住'},
                        {'time': '下午', 'description': '黄鹤楼VIP专属通道游览'},
                        {'time': '傍晚', 'description': '长江游船晚餐'}
                    ]
                }
            ]
        }
    ]

    display_travel_plans(test_plans, message_id=0)