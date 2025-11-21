import requests
import streamlit as st

class APIClient:
    def __init__(self, base_url="http://localhost:5000"):
        """
        initialize the 客户端
        :param base_url: 后端 API 地址
        """
        self.base_url = base_url

    # =======================
    #  Core API Methods
    # =======================

    def check_health(self):
        """检查后端服务是否在线"""
        try:
            resp = requests.get(f"{self.base_url}/health", timeout=2)
            return resp.status_code == 200
        except:
            return False

    def chat(self, prompt, preferences):
        """
        统一入口：发送用户需求和旅行偏好给后端
        
        :param prompt: 用户输入的文本需求
        :param preferences: 侧边栏的旅行偏好（预算、日期等）
        :return: 后端返回的标准 JSON 响应 (包含 action, content, data)
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "prompt": prompt,
                    "preferences": preferences
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"后端返回错误: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"发送需求失败: {str(e)}")
            return None
